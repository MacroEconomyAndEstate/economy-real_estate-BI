import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

def collect_apt_data(LAWD_CD, DEAL_YMD):
    url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade'
    params = {
        'serviceKey': 'mgI42XcdeI7vPE6g9DoA1A/FJNqS3I5veW1ywg2rGd0R/7PzzTXPyvtKAO6gIKdLavcz9RHt2va2VkG0mmfYRg==',
        'LAWD_CD': LAWD_CD,
        'DEAL_YMD': DEAL_YMD
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def parse_xml(xml_data, original_region_name):
    root = ET.fromstring(xml_data)
    apt_data = []

    for item in root.findall('.//item'):
        region_name = original_region_name
        if region_name == '세종특별자치시 해밀동':
            region_name = '세종특별자치시'
        legal_dong = item.find('법정동').text if item.find('법정동') is not None else None
        if legal_dong is not None:
            region_name = f"{region_name} {legal_dong}".replace('  ', ' ')

        deal_amount = item.find('거래금액').text.strip() if item.find('거래금액') is not None else None
        deal_amount = int(deal_amount.replace(',', '').replace(' ', '')) if deal_amount is not None else None

        legal_dong = item.find('법정동').text if item.find('법정동') is not None else None

        build_year = item.find('건축년도').text if item.find('건축년도') is not None else None
        if build_year is not None and build_year.isdigit() and int(build_year) > 0:
            build_year = datetime(year=int(build_year), month=1, day=1).year
        else:
            build_year = None
        
        area = item.find('전용면적').text if item.find('전용면적') is not None else None
        area = float(area) if area is not None else None

        jibun = item.find('지번').text if item.find('지번') is not None else None

        regional_code = item.find('지역코드').text if item.find('지역코드') is not None else None
        regional_code = int(regional_code) if regional_code is not None else None
        
        deal_year = item.find('년').text if item.find('년') is not None else None
        deal_month = item.find('월').text if item.find('월') is not None else None
        deal_day = item.find('일').text if item.find('일') is not None else None

        if deal_year and deal_month and deal_day:
            deal_date = datetime(int(deal_year), int(deal_month), int(deal_day))
        else:
            deal_date = None

        apt_data.append({
            'price': deal_amount,
            'build_year': build_year,
            'date': deal_date,
            'legal_dong': legal_dong,
            'area': area,
            'jibun': jibun,
            'region_code': regional_code,
            'region_name' : region_name
        })
    return apt_data

def main():
    data = pd.read_csv("법정동코드.csv", encoding="cp949")
    code_name_map = dict(zip(data['code'], data['name']))

    LAWD_CD_list = data['code'].tolist()

    dates = [f"{year}{month:02d}" for year in range(2006, 2024) for month in range(1, 13)]

    all_data = pd.DataFrame()
    for LAWD_CD in LAWD_CD_list:
        region_name = code_name_map.get(LAWD_CD)
        for DEAL_YMD in dates:
            print(f"지역코드: {LAWD_CD} - 날짜: {DEAL_YMD}")
            xml_data = collect_apt_data(LAWD_CD, DEAL_YMD)
            if xml_data:
                apt_data = parse_xml(xml_data, region_name)
                df = pd.DataFrame(apt_data)
                all_data = pd.concat([all_data, df], ignore_index=True)
        
        all_data.to_csv("test_temp.csv", index=False)

    all_data['build_year'] = all_data['build_year'].astype('Int64').replace({pd.NA: None})
    all_data['region_name'] = all_data['region_name'].str.replace(r'\s+', ' ', regex=True)


    all_data.to_csv("test.csv", index=False, encoding='utf-8-sig')


if __name__ == "__main__":
    main()
