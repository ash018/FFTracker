

def get_supp_details(supp):
    return {
        'id': supp.id,
        'subject': supp.subject,
        'description': supp.description,
        'date_created': supp.date_created,
        'status': supp.status,
    }


def get_supp_dict_list(supp_list):
    supp_dict_list = []
    for supp in supp_list:
        supp_dict_list.append(get_supp_details(supp))
    return supp_dict_list

