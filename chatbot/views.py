from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json

from .pdf_reader import extract_text
from .ai_service import generate_sector_notes, answer_question, get_sector_detail
from .models import Chat
from chatbot.notes_export import generate_notes_pdf
from chatbot.email_service import send_daily_summary_email

# PDF text तात्पुरता store करायला
_pdf_text_cache = {}


@login_required
def chat_page(request):
    chats = Chat.objects.filter(user=request.user).order_by("-created_at")[:20]
    return render(request, "chat.html", {"chats": chats})


@csrf_exempt
@login_required
def upload_pdf(request):
    if request.method == "POST":
        try:
            if 'pdf' not in request.FILES:
                return JsonResponse({"error": "No PDF file received"}, status=400)

            pdf_file = request.FILES['pdf']
            text = extract_text(pdf_file)

            if not text or len(text.strip()) < 50:
                return JsonResponse({
                    "error": "Could not extract text from this PDF. Please use a text-based PDF."
                })

            # Cache the text for sector detail calls
            user_key = str(request.user.id)
            _pdf_text_cache[user_key] = text

            # Session मध्ये newspaper info save करा
            request.session['newspaper_date'] = datetime.now().strftime('%d %B %Y')
            request.session['newspaper_name'] = 'Indian Express'
            request.session['sector_notes'] = {}
            request.session.modified = True

            # Generate all sector notes
            notes = generate_sector_notes(text)

            Chat.objects.create(
                user=request.user,
                message=f"PDF: {pdf_file.name}",
                response="Sector-wise notes generated."
            )
            return JsonResponse({"sectors": notes, "filename": pdf_file.name})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST only"}, status=405)


@csrf_exempt
@login_required
def sector_detail(request):
    """एका sector साठी detailed notes"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            sector = data.get("sector", "").strip()

            if not sector:
                return JsonResponse({"error": "No sector specified"}, status=400)

            user_key = str(request.user.id)
            text = _pdf_text_cache.get(user_key, "")

            if not text:
                return JsonResponse({"error": "No PDF loaded. Please upload a PDF first."}, status=400)

            detail = get_sector_detail(text, sector)

            # Session मध्ये sector notes save करा (PDF download + email साठी)
            if 'sector_notes' not in request.session:
                request.session['sector_notes'] = {}
            request.session['sector_notes'][sector] = detail
            request.session.modified = True

            return JsonResponse({"detail": detail, "sector": sector})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST only"}, status=405)


@csrf_exempt
@login_required
def chat_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()

            if not message:
                return JsonResponse({"error": "Empty message"}, status=400)

            reply = answer_question(message)

            Chat.objects.create(
                user=request.user,
                message=message,
                response=reply
            )
            return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST only"}, status=405)


@login_required
def download_notes_pdf(request):
    """GET /download-notes/ — Session मधून notes घेतो आणि PDF download करतो"""

    all_notes = request.session.get('sector_notes', {})

    # Optional: specific sectors filter
    sectors_param = request.GET.get('sectors', '')
    if sectors_param:
        selected = [s.strip() for s in sectors_param.split(',')]
        all_notes = {k: v for k, v in all_notes.items() if k in selected}

    if not all_notes:
        return HttpResponse(
            'कोणतेही notes नाहीत. आधी PDF upload करा आणि sector buttons click करा.',
            status=400
        )

    newspaper_date = request.session.get('newspaper_date', '')
    newspaper_name = request.session.get('newspaper_name', 'Indian Express')

    try:
        pdf_bytes = generate_notes_pdf(
            sector_notes=all_notes,
            newspaper_date=newspaper_date,
            newspaper_name=newspaper_name,
        )
        filename = f'CAIS_Notes_{newspaper_date.replace(" ", "_") or "today"}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return HttpResponse(f'PDF generate error: {str(e)}', status=500)


@csrf_exempt
@login_required
def send_email_summary(request):
    """POST /send-email/ — Body: {"email": "user@gmail.com", "attach_pdf": true}"""

    if request.method != 'POST':
        return JsonResponse({'error': 'POST request हवा'}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        body = {}

    to_email = body.get('email') or (request.user.email if request.user.is_authenticated else '')
    attach_pdf = body.get('attach_pdf', True)

    if not to_email:
        return JsonResponse({'success': False, 'message': 'Email address द्या'}, status=400)

    all_notes = request.session.get('sector_notes', {})
    if not all_notes:
        return JsonResponse(
            {'success': False, 'message': 'Notes नाहीत. आधी PDF upload करा आणि sectors click करा.'},
            status=400
        )

    newspaper_date = request.session.get('newspaper_date', '')
    newspaper_name = request.session.get('newspaper_name', 'Indian Express')

    # Optional PDF attachment
    pdf_bytes = None
    if attach_pdf:
        try:
            pdf_bytes = generate_notes_pdf(
                sector_notes=all_notes,
                newspaper_date=newspaper_date,
                newspaper_name=newspaper_name,
            )
        except Exception:
            pdf_bytes = None  # PDF नाही तरी email पाठवतो

    result = send_daily_summary_email(
        sector_notes=all_notes,
        newspaper_date=newspaper_date,
        newspaper_name=newspaper_name,
        to_emails=[to_email],
        attach_pdf=pdf_bytes,
    )

    return JsonResponse(result)