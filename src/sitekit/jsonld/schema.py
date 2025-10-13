def new(type_: str = "Restaurant"):
    out = {
        "@context": "https://schema.org",
        "@type": type_,
        "name": "",
        "image": "",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "",
            "addressLocality": "",
            "postalCode": "",
            "addressCountry": "",
        },
        "telephone": "",
        "url": "",
        "openingHours": [],
    }

    if type_ == "Restaurant":
        out["servesCuisine"] = ["Italiana", "Pesce", "Carne", "Veneziana"]


    return out