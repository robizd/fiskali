from decimal import Decimal

import kasa.fisk as fisk


def get_zki(certifikat, lozinka, oib_tvrtke, vrijeme_izdavanja,
            broj_racuna, oznaka_poslovnog_prostora, oznaka_naplatnog_uredaja, ukupni_iznos):

    try:
        zki = fisk.zastitni_kod(oib_tvrtke,
                                vrijeme_izdavanja.strftime('%d.%m.%YT%H:%M:%S'),
                                str(broj_racuna),
                                oznaka_poslovnog_prostora,
                                str(oznaka_naplatnog_uredaja),
                                str(ukupni_iznos),
                                certifikat,
                                lozinka)
    except Exception as e:
        zki = ''

    return zki


def get_jir(certifikat, lozinka, oib_tvrtke, oib_operatera, u_sustavu_pdv, nacin_placanja, vrijeme_izdavanja,
            broj_racuna, oznaka_poslovnog_prostora, oznaka_naplatnog_uredaja, nak_dost, ukupni_iznos,
            pdv_osnovica_porez_ukupno):

    greska = 'N'
    jir = ''
    errors = []
    racun_reply = ''

    # Ako nije prošla inicijalizacija certifikata, odmah izađi iz ove funkcije
    try:
        fisk.FiskInit.init(certifikat, lozinka)
    except Exception as e:
        greska = 'D'
        errors.append(str(e))
        return {'greska': greska, 'greska_text': errors, 'jir': jir}

    lista_poreza = []
    for key in pdv_osnovica_porez_ukupno:
        lista_poreza.append(fisk.Porez({"Stopa": "{0:.02f}".format(Decimal(key)),
                                        "Osnovica": "{0:.02f}".format(pdv_osnovica_porez_ukupno[key]['osnovica']),
                                        "Iznos": "{0:.02f}".format(pdv_osnovica_porez_ukupno[key]['porez'])}))

    racun = fisk.Racun(data={"Oib": oib_tvrtke,
                             "USustPdv": str(u_sustavu_pdv).lower(),
                             "DatVrijeme": vrijeme_izdavanja.strftime('%d.%m.%YT%H:%M:%S'),  # "26.10.2013T23:50:00",
                             "BrRac": fisk.BrRac({"BrOznRac": str(broj_racuna),
                                                  "OznPosPr": oznaka_poslovnog_prostora,
                                                  "OznNapUr": str(oznaka_naplatnog_uredaja)}),
                             "Pdv": lista_poreza,
                             "IznosUkupno": str(ukupni_iznos),
                             "NacinPlac": nacin_placanja,
                             "OibOper": oib_operatera,
                             "NakDost": str(nak_dost).lower()})

    racun.OznSlijed = "N"

    racunZahtjev = fisk.RacunZahtjev(racun)

    try:
        racun_reply = racunZahtjev.execute()
    except Exception as e:
        errors.append(str(e))

    if racun_reply:
        jir = racun_reply
        # Log
        print("JIR is: " + racun_reply)
    else:
        greska = 'D'
        errors.append(racunZahtjev.get_last_error())
        # Log
        print("RacunZahtjev reply errors:")
        for error in errors:
            print(error)

    fisk.FiskInit.deinit()

    return {'greska': greska, 'greska_text': errors, 'jir': jir}
