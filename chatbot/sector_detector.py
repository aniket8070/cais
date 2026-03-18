def detect_sector(text):

    sectors = {
        "Polity": ["constitution","parliament","supreme court","bill"],
        "Economy": ["gdp","inflation","budget","bank"],
        "Environment": ["climate","forest","biodiversity","wildlife"],
        "Science & Technology": ["ai","space","technology","research"],
        "International Relations": ["un","treaty","global","summit"],
        "Social Issues": ["education","health","poverty"],
        "Defence": ["military","army","navy","missile"]
    }

    for sector, keywords in sectors.items():

        for word in keywords:

            if word in text.lower():

                return sector

    return "General"