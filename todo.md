1. remove all links from markdown content.
for instance:


![](https://ugurokullari.k12.tr/uploads/2024/02/16/asdf-479-288.webp)Okul Öncesinde ASDF Eğitim Modeli

ASDF, öğrencilerin akademik, sosyal, duygusal ve fiziksel gelişimini destekleyen Uğur Okullarına özgü bir eğitim modelidir.

![](https://ugurokullari.k12.tr/uploads/2024/02/16/asdf.webp)
![](https://ugurokullari.k12.tr/assets/img/loader.png)


Should be:

Okul Öncesinde ASDF Eğitim Modeli

ASDF, öğrencilerin akademik, sosyal, duygusal ve fiziksel gelişimini destekleyen Uğur Okullarına özgü bir eğitim modelidir.


But some should stay inside:
## Uğur Okulları

26 Kasım 1968’de Laleli’de ilk dersini vererek öğrencilerini üniversiteye hazırlayan Uğur Dershaneleri bugün, dönüştüğü Uğur Okulları ile Türkiye’nin her noktasında, konusunda uzman öğretmenleri ile okul öncesinden lise son sınıfa kadar Türkiye’nin en donanımlı eğitim olanaklarını sunmaktadır. Okul öncesinden itibaren insani değerlerle donatılmış; sorgulayan, araştıran, üreten nesiller yetiştirmeyi amaçlayan Uğur Okulları, lise ve üniversitelere hazırlıkta bu çağa uygun modeller ve programlar konusunda kendi içinde başlattığı yarışı tüm hızıyla devam ettirmektedir.

![https://www.bauglobal.com/](https://ugurokullari.k12.tr/uploads/2024/02/28/29-1-1.webp)

3 kıtada, 11 ülkeye yayılan 9 üniversite, 4 dil okulu, 2 K12 okulu ile **dünya eğitimine katkı sağlayan** uluslararası bir eğitim ağıdır.

https://www.bauglobal.com/

Should be:
## Uğur Okulları

26 Kasım 1968’de Laleli’de ilk dersini vererek öğrencilerini üniversiteye hazırlayan Uğur Dershaneleri bugün, dönüştüğü Uğur Okulları ile Türkiye’nin her noktasında, konusunda uzman öğretmenleri ile okul öncesinden lise son sınıfa kadar Türkiye’nin en donanımlı eğitim olanaklarını sunmaktadır. Okul öncesinden itibaren insani değerlerle donatılmış; sorgulayan, araştıran, üreten nesiller yetiştirmeyi amaçlayan Uğur Okulları, lise ve üniversitelere hazırlıkta bu çağa uygun modeller ve programlar konusunda kendi içinde başlattığı yarışı tüm hızıyla devam ettirmektedir.

3 kıtada, 11 ülkeye yayılan 9 üniversite, 4 dil okulu, 2 K12 okulu ile **dünya eğitimine katkı sağlayan** uluslararası bir eğitim ağıdır.

https://www.bauglobal.com/


2. Remove some static text appears in scraping
There is a text, maybe part of html that appears in the markdown: "PreviousNext". it should be removed before saving.



