import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from chopee.models import Category, Product, Review

class Command(BaseCommand):
    help = "Seeds the database with realistic Shopee-like e-commerce dummy data"

    def handle(self, *args, **options):
        self.stdout.write("Cleaning database...")
        # Clean current tables to avoid duplicate key issues on re-run
        Review.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        
        # Keep superuser, but clean custom dummy users
        dummy_usernames = ['customer1', 'buyer_demo', 'chopee_fan', 'somchai_dev', 'nattapong']
        User.objects.filter(username__in=dummy_usernames).delete()

        self.stdout.write("Creating categories...")
        categories_data = [
            {"name": "มือถือและอุปกรณ์", "icon": "📱", "slug": "mobile-gadgets"},
            {"name": "คอมพิวเตอร์และอุปกรณ์", "icon": "💻", "slug": "electronics"},
            {"name": "แฟชั่นผู้ชาย", "icon": "👕", "slug": "fashion-men"},
            {"name": "เครื่องใช้ในบ้าน", "icon": "🏠", "slug": "home-living"},
            {"name": "ความงามและเครื่องสำอาง", "icon": "💄", "slug": "beauty-care"},
            {"name": "อาหารและเครื่องดื่ม", "icon": "🍜", "slug": "food-beverages"},
        ]

        categories = {}
        for cat_info in categories_data:
            cat = Category.objects.create(
                name=cat_info["name"],
                icon=cat_info["icon"],
                slug=cat_info["slug"]
            )
            categories[cat_info["slug"]] = cat

        self.stdout.write("Creating dummy users for reviews...")
        dummy_users = []
        user_passwords = {}
        for username in dummy_usernames:
            user = User.objects.create_user(
                username=username,
                email=f"{username}@chopee.com",
                password="password123"
            )
            dummy_users.append(user)
            user_passwords[username] = "password123"

        # Create one standard default customer with simple credentials
        default_buyer = User.objects.create_user(
            username="buyer",
            email="buyer@chopee.com",
            password="password123"
        )
        dummy_users.append(default_buyer)
        self.stdout.write(self.style.SUCCESS("Created demo user: Username: 'buyer', Password: 'password123'"))

        self.stdout.write("Creating products...")
        products_data = [
            # Mobile & Gadgets
            {
                "name": "หูฟังบลูทูธไร้สาย Pro 5 TWS Noise Cancelling",
                "description": "หูฟังบลูทูธไร้สาย TWS Pro 5 เสียงระดับพรีเมียม เบสหนักแน่น\n\nฟีเจอร์เด่น:\n- ระบบตัดเสียงรบกวนรอบข้าง Active Noise Cancellation (ANC)\n- เชื่อมต่อบลูทูธ 5.3 รวดเร็ว เสถียร ประหยัดพลังงาน\n- ควบคุมด้วยระบบสัมผัสอัจฉริยะที่ก้านหูฟัง\n- แบตเตอรี่ใช้งานได้ยาวนานถึง 24 ชั่วโมงพร้อมเคสชาร์จ\n- กันน้ำระดับ IPX5 ใส่ออกกำลังกายได้สบาย\n\nอุปกรณ์ในกล่อง:\n1. หูฟัง Pro 5 (ซ้าย-ขวา)\n2. เคสชาร์จพกพา\n3. สายชาร์จ Type-C\n4. คู่มือการใช้งาน",
                "price": 399.00,
                "original_price": 799.00,
                "discount_percentage": 50,
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop&q=60",
                "category": categories["mobile-gadgets"],
                "rating": 4.8,
                "sold_count": 520,
                "location": "กรุงเทพมหานคร",
                "stock": 140
            },
            {
                "name": "เคสซิลิโคนกันกระแทก Premium Matte สำหรับ iPhone 14/15 Pro Max",
                "description": "เคสโทรศัพท์ซิลิโคนแบบด้านเนื้อนุ่มคุณภาพสูง ป้องกันกล้องและขอบหน้าจออย่างหนาพิเศษ\n\nคุณสมบัติ:\n- ป้องกันการตกกระแทกระดับทหาร (Military Grade Drop Protection)\n- ผิวสัมผัสเนื้อแมตต์ ป้องกันรอยนิ้วมือและคราบมันได้เป็นอย่างดี\n- ขอบรอบกล้องยกสูงขึ้น 1.5 มม. ปกป้องเลนส์กล้องอย่างสมบูรณ์แบบ\n- ขอบด้านในบุด้วยไมโครไฟเบอร์นุ่ม ไม่ทำให้เครื่องเกิดรอยขนแมว\n- รองรับระบบชาร์จไร้สายโดยไม่ต้องถอดเคส",
                "price": 99.00,
                "original_price": 199.00,
                "discount_percentage": 50,
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&auto=format&fit=crop&q=60",
                "category": categories["mobile-gadgets"],
                "rating": 4.7,
                "sold_count": 1280,
                "location": "นนทบุรี",
                "stock": 450
            },
            {
                "name": "แท่นชาร์จไร้สาย Fast Wireless Charger 3-in-1 พับเก็บได้ 15W",
                "description": "แท่นชาร์จไร้สายอเนกประสงค์แบบ 3-in-1 ชาร์จมือถือ หูฟัง และสมาร์ทวอทช์ได้พร้อมกัน\n\nรายละเอียดสินค้า:\n- รองรับการชาร์จเร็วสูงสุด 15W (ขึ้นอยู่กับอุปกรณ์)\n- ชาร์จอุปกรณ์พร้อมกัน 3 ชิ้นอย่างเป็นระเบียบ ลดปัญหาสายชาร์จรกรุงรัง\n- ออกแบบให้พับเก็บได้ น้ำหนักเบา พกพาสะดวกสำหรับการท่องเที่ยว\n- มีระบบป้องกันความร้อนเกิน ไฟเกิน และไฟฟ้าลัดวงจร ปลอดภัย 100%\n- ไฟ LED แสดงสถานะการชาร์จอย่างชัดเจน",
                "price": 490.00,
                "original_price": 890.00,
                "discount_percentage": 45,
                "image_url": "https://images.unsplash.com/photo-1622445262465-2481c4574875?w=500&auto=format&fit=crop&q=60",
                "category": categories["mobile-gadgets"],
                "rating": 4.9,
                "sold_count": 230,
                "location": "กรุงเทพมหานคร",
                "stock": 80
            },
            
            # Computers & Electronics
            {
                "name": "คีย์บอร์ดกลไก Mechanical Keyboard RGB Blue Switch 87 คีย์",
                "description": "คีย์บอร์ดกลไกแมคคานิคอลไฟ RGB เปลี่ยนสีไฟได้หลากหลายโหมด สัมผัสปุ่มกดสไตล์ Blue Switch เสียงดังพิมพ์สนุก\n\nคุณสมบัติ:\n- ปุ่มสวิตช์สัมผัสสองจังหวะ Blue Switch (Clicky) กดสนุก เด้งรับนิ้วได้ดี\n- ไฟพื้นหลัง RGB ปรับเปลี่ยนโหมดไฟได้ 18 รูปแบบ และปรับความสว่างได้\n- ฟังก์ชัน Anti-Ghosting กดพร้อมกันได้ทุกปุ่ม ไม่สะดุดทุกการกด\n- คีย์แคปแบบ Double-shot Injection ตัวอักษรคมชัด ไฟลอดสวยงาม ไม่หลุดลอกง่าย\n- เชื่อมต่อผ่านสาย USB หุ้มสายถักยาว 1.5 เมตร แข็งแรงทนทาน",
                "price": 890.00,
                "original_price": 1590.00,
                "discount_percentage": 44,
                "image_url": "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=500&auto=format&fit=crop&q=60",
                "category": categories["electronics"],
                "rating": 4.8,
                "sold_count": 410,
                "location": "กรุงเทพมหานคร",
                "stock": 95
            },
            {
                "name": "เมาส์ไร้สายเพื่อสุขภาพ Ergonomic Wireless Mouse 2.4G Silent Click",
                "description": "เมาส์แนวตั้งไร้สายออกแบบตามหลักการยศาสตร์ ช่วยปกป้องข้อมือ ลดอาการปวดเมื่อยจากการใช้งานคอมพิวเตอร์เวลานาน\n\nรายละเอียดเพิ่มเติม:\n- ทรงแนวตั้งช่วยจัดระเบียบข้อมือให้อยู่ในมุมธรรมชาติ ลดอาการเกร็ง\n- ปุ่มกดไร้เสียง Silent Click เหมาะสำหรับการทำงานในออฟฟิศหรือห้องสมุด\n- เชื่อมต่อไร้สายผ่านสัญญาณ 2.4GHz ระยะการเชื่อมต่อ 10 เมตร\n- ปรับความไวของเมาส์ DPI ได้ 3 ระดับ (800 / 1200 / 1600)\n- ประหยัดพลังงานด้วยระบบ Auto-sleep ปิดการทำงานอัตโนมัติเมื่อไม่ใช้งาน",
                "price": 290.00,
                "original_price": 590.00,
                "discount_percentage": 50,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&auto=format&fit=crop&q=60",
                "category": categories["electronics"],
                "rating": 4.6,
                "sold_count": 890,
                "location": "ชลบุรี",
                "stock": 180
            },
            
            # Men's Fashion
            {
                "name": "เสื้อยืดคอตตอนหนานุ่ม Premium Oversized T-Shirt สีพื้นสตรีท",
                "description": "เสื้อยืดสไตล์เกาหลีโอเวอร์ไซส์ (Oversized Fit) ผลิตจากเนื้อผ้าคอตตอนฝ้ายเกรดพิเศษ 100% สวมใส่สบายระบายอากาศได้ดี\n\nลักษณะเนื้อผ้า:\n- ผ้าหนา 230 แกรม กำลังพอดี ไม่บางไม่หนาเกินไป ทรงสวย อยู่ทรง\n- สัมผัสนุ่มละมุนผิว ระบายเหงื่อและอากาศได้ดีเยี่ยม\n- สีพื้นยอดนิยม ดำ ขาว เทา ครีม แมทช์ชุดง่ายกับกางเกงทุกแบบ\n- เย็บตะเข็บคู่อย่างดีรอบคอและไหล่เพื่อความทนทาน ไม่ย้วยง่าย",
                "price": 199.00,
                "original_price": 390.00,
                "discount_percentage": 49,
                "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=60",
                "category": categories["fashion-men"],
                "rating": 4.9,
                "sold_count": 1450,
                "location": "ปทุมธานี",
                "stock": 600
            },
            {
                "name": "กางเกงคาร์โก้ขายาวสตรีท Cargo Pants 6 กระเป๋าอเนกประสงค์",
                "description": "กางเกงคาร์โก้ขายาวทรงสวย สไตล์สตรีทแฟชั่นยอดนิยม เย็บช่องกระเป๋าหนาพิเศษถึง 6 ช่อง\n\nคุณลักษณะสินค้า:\n- ผลิตจากผ้าเวสปอยท์คอตตอน (West Point Cotton) หนา ทนทานเป็นพิเศษ\n- ฟอกนุ่มแล้ว สีไม่ตก ผ้าไม่ยับง่าย ไม่เกิดขุยหลังซัก\n- ทรงกระบอกตรง ใส่สบาย ไม่กระชับอึดอัด ลุกนั่งได้คล่องตัว\n- กระเป๋าข้างขนาดใหญ่ติดกระดุมแป๊กนิรภัย ปลอดภัยสำหรับกระเป๋าสตางค์และมือถือ",
                "price": 450.00,
                "original_price": 890.00,
                "discount_percentage": 49,
                "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop&q=60",
                "category": categories["fashion-men"],
                "rating": 4.7,
                "sold_count": 340,
                "location": "สมุทรปราการ",
                "stock": 110
            },
            
            # Home & Living
            {
                "name": "แก้วน้ำเก็บอุณหภูมิสแตนเลส Double Wall Tyeso ขนาด 30 ออนซ์",
                "description": "แก้วน้ำเก็บอุณหภูมิความเย็นยาวนาน 24 ชั่วโมง ความร้อน 12 ชั่วโมง ผลิตจากเหล็กไร้สนิมสแตนเลส SUS304 แข็งแรงปลอดภัยอาหาร\n\nคุณประโยชน์:\n- เทคโนโลยีผนังแก้วสองชั้นพร้อมสุญญากาศ (Double-Wall Vacuum Isolation)\n- ป้องกันไอน้ำเกาะข้างแก้วโดยสิ้นเชิง กระเป๋าไม่เปียกชื้น\n- ฝาเกลียวปิดสนิทพร้อมยางซิลิโคนกันน้ำหก และช่องสำหรับใส่หลอดดูด\n- ปากแก้วกว้างล้างทำความสะอาดง่าย ไม่สะสมแบคทีเรียหรือกลิ่นตกค้าง\n- ขนาดพอดีกับช่องวางแก้วบนรถยนต์ทั่วไป",
                "price": 250.00,
                "original_price": 490.00,
                "discount_percentage": 49,
                "image_url": "https://images.unsplash.com/photo-1577937927133-66ef06acdf18?w=500&auto=format&fit=crop&q=60",
                "category": categories["home-living"],
                "rating": 4.9,
                "sold_count": 980,
                "location": "กรุงเทพมหานคร",
                "stock": 250
            },
            {
                "name": "พัดลมพกพาขนาดเล็ก Mini Desktop USB Fan ปรับแรงลม 3 ระดับ",
                "description": "พัดลมขนาดกะทัดรัดสำหรับวางโต๊ะทำงานหรือถือพกพาสะดวก ลมแรงจัด ชาร์จง่ายผ่าน USB สายแคมป์ปิ้งต้องมี\n\nข้อมูลจำเพาะ:\n- มอเตอร์ทองแดง Brushless เงียบสนิท ไม่มีเสียงดังรบกวนสมาธิทำงาน\n- ปรับระดับความแรงลมได้ 3 ระดับ (เบา, ปานกลาง, แรง)\n- แบตเตอรี่ลิเธียมในตัวความจุ 2000mAh ใช้งานได้นาน 3-8 ชั่วโมงต่อการชาร์จหนึ่งครั้ง\n- สามารถปรับองศาก้ม-เงยได้ 180 องศาเพื่อกระจายแรงลม\n- ฝาครอบพัดลมถอดล้างทำความสะอาดได้อย่างสะดวกสบาย",
                "price": 120.00,
                "original_price": 299.00,
                "discount_percentage": 60,
                "image_url": "https://images.unsplash.com/photo-1618944913480-b67ee16d7b77?w=500&auto=format&fit=crop&q=60",
                "category": categories["home-living"],
                "rating": 4.5,
                "sold_count": 1600,
                "location": "เชียงใหม่",
                "stock": 350
            },
            
            # Beauty & Care
            {
                "name": "เซรั่มไฮยาเข้มข้นเติมน้ำผิว Hyaluronic Acid Booster Serum 30ml",
                "description": "เซรั่มบำรุงผิวหน้าไฮยาลูรอนิกบริสุทธิ์เข้มข้นสูง ช่วยฟื้นบำรุงผิวแห้งขาดน้ำ ให้กลับมาเรียบเนียนอิ่มฟูและมีน้ำมีนวล\n\nผลลัพธ์การใช้งาน:\n- เติมความชุ่มชื้นให้ผิวชั้นนอกทันทีหลังใช้ ป้องกันผิวแห้งเป็นขุย\n- ล็อกความชุ่มชื้นได้ยาวนานถึง 72 ชั่วโมง\n- ช่วยลดเลือนริ้วรอยร่องลึก ผิวดูอิ่มเด้งกระชับและมีความยืดหยุ่น\n- ซึมซาบเข้าสู่ผิวได้อย่างรวดเร็ว ไม่เหนียวเหนอะหนะหน้า\n- ปราศจากพาราเบน แอลกอฮอล์ และน้ำหอม อ่อนโยนต่อผิวแพ้ง่ายมาก",
                "price": 350.00,
                "original_price": 790.00,
                "discount_percentage": 55,
                "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&auto=format&fit=crop&q=60",
                "category": categories["beauty-care"],
                "rating": 4.8,
                "sold_count": 670,
                "location": "กรุงเทพมหานคร",
                "stock": 190
            },
            {
                "name": "ครีมกันแดดคุมมันเบาสบายหน้า Watery Sunscreen SPF50+ PA++++",
                "description": "โลชั่นป้องกันแสงแดดสูตรน้ำบางเบาดุจน้ำนม ป้องกันผิวคล้ำเสียและริ้วรอยก่อนวัยจากแสงแดดได้อย่างมีประสิทธิภาพสูงสุด\n\nจุดเด่น:\n- ดัชนีการปกป้อง SPF50+ PA++++ ป้องกันรังสี UVA และ UVB ได้อย่างมีประสิทธิภาพ\n- สูตรคุมมันกันน้ำกันเหงื่อ (Oil Control & Sweat-resistant)\n- เนื้อเจลสัมผัสน้ำนม แตกตัวเป็นน้ำทันทีที่ทา ซึมไว เบาสบายผิวหน้า ไม่หนักหน้า\n- มีไฮยาลูรอนและวิตามินอี บำรุงผิวให้ชุ่มชื้นกระจ่างใสระหว่างวัน\n- ไม่ทิ้งคราบขาวหรือทำให้เกิดสิวอุดตัน เหมาะสำหรับทาก่อนแต่งหน้า",
                "price": 299.00,
                "original_price": 499.00,
                "discount_percentage": 40,
                "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&auto=format&fit=crop&q=60",
                "category": categories["beauty-care"],
                "rating": 4.8,
                "sold_count": 830,
                "location": "ชลบุรี",
                "stock": 200
            },
            
            # Food & Beverages
            {
                "name": "ผงชาเขียวมัทฉะแท้เกรดพรีเมียม Organic Uji Matcha Powder 100g",
                "description": "ผงมัทฉะแท้ 100% นำเข้าจากเมืองอูจิ จังหวัดเกียวโต ประเทศญี่ปุ่น แหล่งผลิตชาเขียวที่ดีที่สุดในโลก\n\nรายละเอียดสินค้า:\n- ชาเขียวออร์แกนิกเกรดพรีเมียม คัดเฉพาะใบชาอ่อนยอดแรก (First Harvest)\n- บดละเอียดด้วยโม่หินธรรมชาติแบบญี่ปุ่นโบราณ รักษาคุณค่าและสีเขียวมรกต\n- รสชาติอูมามิกลมกล่อม มีรสขมปลายลิ้นเล็กน้อย กลิ่นหอมใบชาคั่วละมุน\n- ปราศจากการปรุงแต่งกลิ่น สีสังเคราะห์ หรือสารกันเสีย\n- เหมาะสำหรับการชง มัทฉะลาเต้เย็น, ชาใส หรือผสมทำเบเกอรี่ ขนมเค้ก",
                "price": 180.00,
                "original_price": 350.00,
                "discount_percentage": 48,
                "image_url": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=500&auto=format&fit=crop&q=60",
                "category": categories["food-beverages"],
                "rating": 4.9,
                "sold_count": 450,
                "location": "เชียงใหม่",
                "stock": 120
            }
        ]

        dummy_comments = [
            "สินค้าดีมากๆ ครับ ตรงปกทุกอย่าง การจัดส่งทำได้รวดเร็วมาก แพ็กสินค้ามาอย่างดี แนะนำร้านนี้เลยครับ!",
            "ส่งไวมากค่ะ คุ้มค่าคุ้มราคา คุณภาพสินค้าถือว่าดีมาก ลองใช้งานดูแล้วไม่มีปัญหาอะไร แนะนำเลยค่าา 👍",
            "ได้รับสินค้าเรียบร้อยดี จัดส่งใช้เวลาไม่นาน แพ็กของใส่บับเบิ้ลกันกระแทกมาแน่นหนา บริการขนส่งดีมากค่ะ",
            "ได้รับของตรงตามสเปกเลยครับ ลองเทสแล้วใช้งานได้ดีปกติ ราคาถูกกว่าหน้าร้านเยอะ คุ้มค่าเงินมาก",
            "ประทับใจค่ะ สินค้าสวยงาม ถูกใจมาก ราคาไม่แพง ค่าส่งฟรีด้วย เอาไว้โอกาสหน้าจะมาอุดหนุนอีกแน่นอนค่ะ"
        ]

        for p_info in products_data:
            product = Product.objects.create(
                name=p_info["name"],
                description=p_info["description"],
                price=p_info["price"],
                original_price=p_info["original_price"],
                discount_percentage=p_info["discount_percentage"],
                image_url=p_info["image_url"],
                category=p_info["category"],
                rating=p_info["rating"],
                sold_count=p_info["sold_count"],
                location=p_info["location"],
                stock=p_info["stock"]
            )
            
            # Create 3-4 random reviews for this product
            reviewers = random.sample(dummy_users, k=random.randint(3, 5))
            for reviewer in reviewers:
                Review.objects.create(
                    product=product,
                    user=reviewer,
                    rating=random.choice([4, 5]),
                    comment=random.choice(dummy_comments)
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
