import requests
api_url="https://3hwowx4270-dsn.algolia.net/1/indexes/*/queries?X-Algolia-API-Key=4c4f62629d66d4e9463ddb94b9217afb&X-Algolia-Application-Id=3HWOWX4270&X-Algolia-Agent=Algolia%20for%20vanilla%20JavaScript%202.9.7"
import requests

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-type': 'application/x-www-form-urlencoded',
    'Origin': 'https://www.homecentre.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.homecentre.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="141", "Not?A_Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

data = '{"requests":[{"indexName":"prod_uae_homecentre_Product","params":"query=*&hitsPerPage=42&page=0&facets=*&facetFilters=%5B%22inStock%3A1%22%2C%22approvalStatus%3A1%22%2C%22allCategories%3Afurniture-bedroom%22%2C%22badge.title.en%3A-LASTCHANCE%22%5D&getRankingInfo=1&clickAnalytics=true&attributesToHighlight=null&analyticsTags=%5B%22furniture-bedroom%22%2C%22en%22%2C%22Webmobile%22%5D&attributesToRetrieve=concept%2CmanufacturerName%2Curl%2C333WX493H%2C345WX345H%2C505WX316H%2C550WX550H%2C499WX739H%2Cbadge%2Cname%2Csummary%2CwasPrice%2Cprice%2CemployeePrice%2CshowMoreColor%2CproductType%2CchildDetail%2Csibiling%2CthumbnailImg%2CgallaryImages%2CisConceptDelivery%2CextProdType%2CreviewAvgRating%2CreferencesAvailable%2CitemType%2CbaseProductId%2CflashSaleData%2CcategoryName%2CallCategories%2ConlineDate&numericFilters=price%20%3E%200.9&query=*&maxValuesPerFacet=500&tagFilters=%5B%5B%22homecentre%22%2C%22magiccarpets%22%2C%22citycorp%22%2C%22cottonhome%22%2C%22emiratesdimlaj%22%2C%22element%22%2C%22cottonhomedropship%22%2C%22hckhiara%22%2C%22hckatei%22%2C%22hcfissman%22%2C%22dealsforless%22%2C%22hcnavo%22%2C%22hclanny%22%2C%22hcalmakaan%22%2C%22hcluna%22%2C%22hcramrod%22%2C%22hchomecanvas%22%2C%22heritaji%22%2C%22anoc%22%2C%22homekode%22%2C%22swin%22%2C%22cortina%22%2C%22curate%22%2C%22wisewell%22%2C%22knothome%22%2C%22hartmann%22%2C%22artezaar%22%2C%22rattanhouse%22%2C%22yourock%22%2C%22aroma247%22%2C%22yataidecor%22%2C%22houseofflair%22%2C%22tramontina%22%2C%22myts%22%2C%22royalsaraya%22%2C%22modernchairs%22%2C%22lilacs%22%2C%22slabhouse%22%2C%22houseofserene%22%2C%22larosa%22%2C%22hcjumbodropship%22%2C%22sellingpot%22%2C%22karoo%22%2C%22woodentwist%22%2C%22quesera%22%2C%22pushe%22%2C%22woodgreen%22%2C%22silkycarpets%22%2C%22tajrid%22%2C%22jashanmal%22%2C%22halaitrading%22%2C%22designboxfurniture%22%2C%22finishingtouch%22%2C%22woodculture%22%2C%22indocount%22%2C%22jasani%22%2C%22aljabertrading%22%2C%228thsenses%22%2C%22otath%22%2C%22blu%22%2C%22mourah%22%2C%22coinmaison%22%2C%22parasolinternational%22%2C%22atozfurniture%22%2C%22tagiawoodworks%22%2C%22dixiesboutique%22%2C%22zerowellness%22%2C%22garnergeneral%22%2C%22gautier%22%2C%22h2opureblue%22%2C%22oasiscasual%22%2C%22moonkids%22%2C%22ramshahome%22%2C%22vidaxl%22%2C%22huxberry%22%2C%22homesmiths%22%2C%22hcemax%22%2C%22woodandsteel%22%2C%22mooboohome%22%2C%22breedgetrading%22%2C%22yallahomegym%22%2C%22carpetcentre%22%2C%22brightline%22%2C%22antwork%22%2C%22aryaanvikas%22%2C%22gardenconcept%22%2C%22villahome%22%2C%22aiidadesign%22%2C%22bosq%22%2C%22aptrading%22%2C%22lamac%22%2C%22nader%22%2C%22growhub%22%2C%22smithquinn%22%2C%22hocc%22%2C%22rotai%22%2C%22tabeerhomes%22%2C%22desertriver%22%2C%22bosqds%22%2C%22interbuild%22%2C%22plntd%22%2C%22enzahome%22%2C%22ironyhome%22%2C%22hcwoodentwist%22%2C%22hcbabico%22%2C%22solohome%22%2C%22hcmapyr%22%2C%22luvsaffron%22%2C%22shyconcepts%22%2C%22chateauxme%22%2C%22sol%22%2C%22nayamsleep%22%2C%22hcdesertbeat%22%2C%22ezzro%22%2C%22hassani%22%2C%22algt%22%2C%22plonko%22%2C%22petcorner%22%2C%22karnakhome%22%2C%22hcmahmayi%22%2C%22askona%22%2C%22hcshoemart%22%2C%22oakhouses%22%2C%22bohobliss%22%2C%22shoemarthc%22%2C%22maisonremie%22%2C%22apparel%22%2C%22mebashi%22%2C%22geometryhome%22%2C%22silentnight%22%2C%22nia%22%2C%22sleepwell%22%2C%22wometech%22%2C%22frido%22%2C%22orrohome%22%2C%22lepetit%22%2C%22hcdesertbeatdropship%22%2C%22artcraft%22%2C%22botella%22%2C%22vanityliving%22%2C%22samboxhc%22%2C%22babygrow%22%2C%22botellahc%22%2C%22studiokinza%22%2C%22biggbrandshc%22%2C%22hcbiggbrands%22%2C%22muradreis%22%2C%22mulberryliving%22%2C%22oppdoor%22%2C%22homefigures%22%2C%22bazarkom%22%2C%22touchedeco%22%2C%22thefinishingtouch%22%2C%22studiobliq%22%2C%22keen%22%5D%5D"}]}'

response = requests.post(api_url, headers=headers, data=data)

print(response.text)