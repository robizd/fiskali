import kasa.fisk as fisk
import lxml.etree as et
import ast
from datetime import date, timedelta

#fiskpy initialization !!! must be used for RacunZahtjev
# fisk.FiskInit.init('/home/r/projects/fiskalna/media/certifikati/FISKAL_2.p12', "Pakelmozesve1")
#For production environment
#fisk.FiskInit.init('/path/to/your/key.pem', "kaypassword", '/path/to/your/cert.pem', Ture)


racun = fisk.Racun(data = {"Oib": "55703284647",
              "USustPdv": "true",
              "DatVrijeme": "26.10.2013T23:50:00",
              "BrRac": fisk.BrRac({"BrOznRac": "2", "OznPosPr":"POS2", "OznNapUr":"1"}),
              "Pdv": [fisk.Porez({"Stopa":"25.00", "Osnovica":"100.00", "Iznos":"25.00"}), fisk.Porez({"Stopa":"10.00", "Osnovica":"100.00", "Iznos":"10.00"})],
              "Pnp": [fisk.Porez({"Stopa":"25.00", "Osnovica":"100.00", "Iznos":"25.00"}), fisk.Porez({"Stopa":"10.00", "Osnovica":"100.00", "Iznos":"10.00"})],
              "OstaliPor": [fisk.OstPorez({"Naziv": "Neki porez",  "Stopa":"3.00", "Osnovica":"100.00", "Iznos":"3.00"})],
              "IznosOslobPdv": "100.00",
              "IznosMarza": "100.00",
              "IznosNePodlOpor": "50.00",
              "Naknade": [fisk.Naknada({"NazivN" : "test", "IznosN": "10.00"})],
              "IznosUkupno": "500.00",
              "NacinPlac": "G",
              "OibOper": "12345678901",
              "NakDost": "false",
              "ParagonBrRac": "123-234-12",
              "SpecNamj": "Tekst specijalne namjne"})

#IWe did not supplied required element in constructor so now we set it
racun.OznSlijed = "P"

#Zastitni kod is calculated so print it
print ("ZKI: " + racun.ZastKod)

#change one variable and check new zastitni kod
racun.IznosUkupno = "1233.00"
print ("ZKI: " + racun.ZastKod)

#create Request and send it to server (DEMO) and print reply
racunZahtjev = fisk.RacunZahtjev(racun)
racun_reply = racunZahtjev.execute()
if(racun_reply != False):
    print ("JIR is: " + racun_reply)
else:
    errors = racunZahtjev.get_last_error()
    print ("RacunZahtjev reply errors:")
    for error in errors:
        print (error)

#fiskpy deinitialization - maybe not needed but good for correct garbage cleaning
fisk.FiskInit.deinit()
