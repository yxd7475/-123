from werkzeug.security import generate_password_hash
from app import db
from app.models.models import User, Item

def init_database():
    if User.query.count() == 0:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            real_name='系统管理员',
            role='admin',
            status=True
        )
        db.session.add(admin)
        
        operator = User(
            username='operator',
            password=generate_password_hash('operator123'),
            real_name='仓库操作员',
            role='operator',
            status=True
        )
        db.session.add(operator)
        
        viewer = User(
            username='viewer',
            password=generate_password_hash('viewer123'),
            real_name='查看员',
            role='viewer',
            status=True
        )
        db.session.add(viewer)
        
        receiver = User(
            username='receiver',
            password=generate_password_hash('receiver123'),
            real_name='领取员',
            role='receiver',
            status=True
        )
        db.session.add(receiver)
        
        db.session.commit()
    
    if Item.query.count() == 0:
        sample_items = [
            {
                'item_code': 'ITM001',
                'name': '螺丝刀',
                'specification': 'M6*100mm',
                'model': 'SD-001',
                'unit': '把',
                'unit_price': 15.00,
                'quantity': 100,
                'min_quantity': 20,
                'max_quantity': 500,
                'category': '工具类',
                'location': 'A区-01货架-01层',
                'supplier': '五金工具厂'
            },
            {
                'item_code': 'ITM002',
                'name': '扳手',
                'specification': '8寸',
                'model': 'BW-008',
                'unit': '把',
                'unit_price': 25.00,
                'quantity': 50,
                'min_quantity': 10,
                'max_quantity': 200,
                'category': '工具类',
                'location': 'A区-01货架-02层',
                'supplier': '五金工具厂'
            },
            {
                'item_code': 'ITM003',
                'name': '电缆线',
                'specification': '3*2.5mm²',
                'model': 'DL-0025',
                'unit': '米',
                'unit_price': 8.50,
                'quantity': 500,
                'min_quantity': 100,
                'max_quantity': 2000,
                'category': '电气类',
                'location': 'B区-02货架-01层',
                'supplier': '电缆材料公司'
            },
            {
                'item_code': 'ITM004',
                'name': '安全帽',
                'specification': '标准型',
                'model': 'AQ-001',
                'unit': '顶',
                'unit_price': 35.00,
                'quantity': 30,
                'min_quantity': 20,
                'max_quantity': 100,
                'category': '防护用品',
                'location': 'C区-01货架-01层',
                'supplier': '劳保用品公司'
            },
            {
                'item_code': 'ITM005',
                'name': '润滑油',
                'specification': '5L装',
                'model': 'RH-005',
                'unit': '桶',
                'unit_price': 120.00,
                'quantity': 15,
                'min_quantity': 10,
                'max_quantity': 50,
                'category': '化工类',
                'location': 'D区-01货架-01层',
                'supplier': '化工材料公司'
            }
        ]
        
        for item_data in sample_items:
            item = Item(**item_data)
            db.session.add(item)
        
        db.session.commit()
