



def country_code(country:str):
    codes = {
        "Belgium":"BE",
        "Bulgaria":"BG",
        "Czechia":"CZ",
        "Denmark":"DK",
        "Germany":"DE",
        "Estonia":"EE",
        "Ireland":"IE",
        "Greece":"EL",
        "Spain":"ES",
        "France":"FR",
        "Croatia":"HR",
        "Italy":"IT",
        "Cyprus":"CY",
        "Latvia":"LV",
        "Lithuania":"LT",
        "Luxembourg":"LU",
        "Hungary":"HU",
        "Malta":"MT",
        "Netherlands":"NL",
        "Austria":"AT",
        "Poland":"PL" ,
        "Portugal":"PT",
        "Romania":"RO",
        "Slovenia":"SI",
        "Slovakia":"SK",
        "Finland":"FI",
        "Sweden":"SE",
    }
    country = country.capitalize()
    if country not in codes.keys():
        raise ValueError("Country not known")
    return codes[country]