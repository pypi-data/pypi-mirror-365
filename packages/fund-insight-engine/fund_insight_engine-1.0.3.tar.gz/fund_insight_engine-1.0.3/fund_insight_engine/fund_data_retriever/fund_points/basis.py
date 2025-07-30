from mongodb_controller import COLLECTION_8186

def create_pipeline_point_menu8186(fund_code, date, key):
    return [
        {
            '$match': {
                '펀드코드': fund_code,
                '일자': date
            }
        },
        {
            '$project': {
                '_id': 0,
                key: 1
            }
        }
    ]

def get_point_menu8186(fund_code, date, key):
    pipeline = create_pipeline_point_menu8186(fund_code, date, key)
    cursor = COLLECTION_8186.aggregate(pipeline)
    data = list(cursor)
    return data[0][key]
