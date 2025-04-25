def get_items_for_tab(tab_name):
    if tab_name == 'do_an':
        return [
            {"name": "Cháo lòng", "price": 25000,"image": "assets/food/chao_long.jpg","available": 10},
            {"name": "Cơm sườn", "price": 25000, "image": "assets/food/com_suon.jpg","available": 8},
            {"name": "Bún thịt nướng", "price": 25000, "image": "assets/food/bun_thit_nuong.jpg","available": 12},
            {"name": "Gà xào sả ớt", "price": 25000, "image": "assets/food/ga_xao_sa_ot.jpg","available": 7},
            {"name": "Ếch xào sả ớt", "price": 25000, "image": "assets/food/ech_xao_sa_ot.jpg","available": 5},
            {"name": "Vịt kho gừng", "price": 25000, "image": "assets/food/vit_kho_gung.jpg","available": 6},
        ]
    elif tab_name == 'thuc_uong':
        return [
            {"name": "Trà sữa", "price": 15000, "image": "assets/beverage/tra_sua.jpg","available": 15},
            {"name": "Nước cam", "price": 15000, "image": "assets/beverage/nuoc_cam.jpg","available": 12},
            {"name": "Cà phê", "price": 12000, "image": "assets/beverage/ca_phe.jpg","available": 20},
            {"name": "Soda", "price": 10000, "image": "assets/beverage/soda.jpg","available": 18},
            {"name": "Matcha đá xay", "price": 20000, "image": "assets/beverage/matcha.jpg","available": 9},
        ]
    return []