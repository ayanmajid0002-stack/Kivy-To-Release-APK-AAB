from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Set window size (for testing on PC)
Window.size = (400, 700)

# ============= CONFIGURATION =============
APP_NAME = "Raza Trader"
SHOP_NAME = "RAZA TRADER"
TAGLINE = "Premium Order Taking System"
THANK_YOU_MSG = "Thank you for choosing Raza Trader"
DELIVERY_MSG = "Your order will be delivered within 30 minutes"

# Storage paths (Android compatible)
DATA_FOLDER = '/sdcard/raza_trader_data'
CUSTOMERS_FILE = os.path.join(DATA_FOLDER, "customers.json")
PRODUCTS_FILE = os.path.join(DATA_FOLDER, "products.json")
ORDERS_FILE = os.path.join(DATA_FOLDER, "orders_data.json")
ORDERS_FOLDER = os.path.join(DATA_FOLDER, "orders_images")

# Default Products
DEFAULT_PRODUCTS = [
    {"id": 1, "name": "Chai", "price": 20},
    {"id": 2, "name": "Samosa", "price": 15},
    {"id": 3, "name": "Biscuit", "price": 10},
    {"id": 4, "name": "Pakora", "price": 25},
    {"id": 5, "name": "Coffee", "price": 30},
    {"id": 6, "name": "Toast", "price": 20},
    {"id": 7, "name": "Egg Roll", "price": 35},
    {"id": 8, "name": "Noodles", "price": 50},
    {"id": 9, "name": "Lassi", "price": 40},
    {"id": 10, "name": "Water Bottle", "price": 20}
]

# Initialize folders
def init_folders():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(ORDERS_FOLDER):
        os.makedirs(ORDERS_FOLDER)

# Load/Save functions
customers = {}
products = []
orders = []
order_counter = 1

def generate_order_number():
    global order_counter
    year = datetime.now().strftime('%Y')
    order_num = f"RT-{year}-{order_counter:04d}"
    order_counter += 1
    return order_num

def load_data():
    global customers, products, orders, order_counter
    init_folders()
    
    if os.path.exists(CUSTOMERS_FILE):
        with open(CUSTOMERS_FILE, 'r') as f:
            customers = json.load(f)
    
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r') as f:
            products = json.load(f)
    else:
        products = DEFAULT_PRODUCTS.copy()
        save_products()
    
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            orders = json.load(f)
        if orders:
            try:
                last = orders[-1]['order_num'].split('-')[-1]
                order_counter = int(last) + 1
            except:
                order_counter = len(orders) + 1

def save_customers():
    with open(CUSTOMERS_FILE, 'w') as f:
        json.dump(customers, f)

def save_products():
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f)

def save_orders():
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f)

# PNG Generation
def generate_png(order_num, customer_name, phone, address, cart, total):
    filename = f"order_{order_num.replace('-', '_')}_{customer_name.replace(' ', '_')}.png"
    filepath = os.path.join(ORDERS_FOLDER, filename)
    
    height = 600 + len(cart) * 30
    img = Image.new('RGB', (800, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 30)
        font_normal = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_bold = ImageFont.load_default()
    
    y = 30
    draw.text((400, 40), SHOP_NAME, fill='#e94560', font=font_title, anchor='mm')
    draw.text((400, 75), TAGLINE, fill='#ffffff', font=font_normal, anchor='mm')
    y = 110
    
    draw.text((400, y), f"ORDER {order_num}", fill='#e94560', font=font_bold, anchor='mm')
    y += 40
    
    draw.text((50, y), f"Customer: {customer_name}", fill='#ffffff', font=font_normal)
    y += 25
    draw.text((50, y), f"Phone: {phone}", fill='#ffffff', font=font_normal)
    y += 25
    draw.text((50, y), f"Address: {address[:40]}", fill='#ffffff', font=font_normal)
    y += 25
    draw.text((50, y), datetime.now().strftime('%d %b %Y | %I:%M %p'), fill='#aaaaaa', font=font_normal)
    y += 50
    
    draw.line([(50, y), (750, y)], fill='#e94560', width=1)
    y += 15
    
    for item in cart:
        draw.text((50, y), item['name'][:25], fill='#ffffff', font=font_normal)
        draw.text((550, y), f"x{item['quantity']}", fill='#ffffff', font=font_normal)
        draw.text((680, y), f"Rs.{item['subtotal']}", fill='#ffffff', font=font_normal)
        y += 30
    
    draw.line([(50, y), (750, y)], fill='#e94560', width=1)
    y += 15
    draw.text((680, y), f"TOTAL: Rs.{total}", fill='#e94560', font=font_bold, anchor='mm')
    y += 50
    draw.text((400, y), THANK_YOU_MSG, fill='#4caf50', font=font_normal, anchor='mm')
    y += 30
    draw.text((400, y), DELIVERY_MSG, fill='#e94560', font=font_normal, anchor='mm')
    
    img.save(filepath)
    return filepath

# ============= KIVY UI =============

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.914, 0.271, 0.376, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Header
        header = BoxLayout(size_hint_y=0.15, orientation='vertical')
        header.add_widget(Label(text=SHOP_NAME, font_size=28, color=(0.914, 0.271, 0.376, 1), size_hint_y=0.6))
        header.add_widget(Label(text=TAGLINE, font_size=12, color=(0.7, 0.7, 0.7, 1), size_hint_y=0.4))
        self.add_widget(header)
        
        # Buttons
        btn_layout = GridLayout(cols=1, spacing=12, size_hint_y=0.7)
        
        btn_new = RoundedButton(text="NEW ORDER", font_size=18, color=(1,1,1,1))
        btn_new.bind(on_press=self.new_order)
        btn_layout.add_widget(btn_new)
        
        btn_history = Button(text="ORDER HISTORY", font_size=16, background_color=(0.2, 0.2, 0.3, 1), color=(1,1,1,1))
        btn_history.bind(on_press=self.show_history)
        btn_layout.add_widget(btn_history)
        
        btn_customers = Button(text="CUSTOMER LIST", font_size=16, background_color=(0.2, 0.2, 0.3, 1), color=(1,1,1,1))
        btn_customers.bind(on_press=self.show_customers)
        btn_layout.add_widget(btn_customers)
        
        btn_products = Button(text="PRODUCTS", font_size=16, background_color=(0.2, 0.2, 0.3, 1), color=(1,1,1,1))
        btn_products.bind(on_press=self.manage_products)
        btn_layout.add_widget(btn_products)
        
        self.add_widget(btn_layout)
        
        # Footer
        footer = Label(text="Raza Trader 2025", font_size=10, color=(0.5,0.5,0.5,1), size_hint_y=0.08)
        self.add_widget(footer)
    
    def new_order(self, instance):
        self.parent.current = 'order'
        self.parent.get_screen('order').reset()
    
    def show_history(self, instance):
        self.parent.current = 'history'
        self.parent.get_screen('history').refresh()
    
    def show_customers(self, instance):
        self.parent.current = 'customers'
        self.parent.get_screen('customers').refresh()
    
    def manage_products(self, instance):
        self.parent.current = 'products'
        self.parent.get_screen('products').refresh()

class OrderScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.cart = []
        self.customer_name = ""
        self.customer_phone = ""
        self.customer_address = ""
        
        # Name input
        self.name_input = TextInput(hint_text="Enter Customer Name", size_hint_y=0.08, font_size=16)
        self.add_widget(self.name_input)
        
        self.next_btn = Button(text="Next", size_hint_y=0.08, background_color=(0.914, 0.271, 0.376, 1), color=(1,1,1,1))
        self.next_btn.bind(on_press=self.check_customer)
        self.add_widget(self.next_btn)
        
        # Menu (hidden initially)
        self.menu_layout = GridLayout(cols=2, spacing=8, size_hint_y=0.5)
        
        # Cart display
        self.cart_label = Label(text="Cart Empty", size_hint_y=0.2, color=(0.8,0.8,0.8,1), font_size=14)
        self.add_widget(self.cart_label)
        
        self.finish_btn = Button(text="FINISH ORDER", size_hint_y=0.08, background_color=(0.914, 0.271, 0.376, 1), color=(1,1,1,1))
        self.finish_btn.bind(on_press=self.finish_order)
        self.add_widget(self.finish_btn)
        
        self.back_btn = Button(text="BACK", size_hint_y=0.06, background_color=(0.3,0.3,0.3,1), color=(1,1,1,1))
        self.back_btn.bind(on_press=lambda x: setattr(self.parent, 'current', 'main'))
        self.add_widget(self.back_btn)
    
    def reset(self):
        self.cart = []
        self.customer_name = ""
        self.customer_phone = ""
        self.customer_address = ""
        self.name_input.text = ""
        self.name_input.disabled = False
        self.next_btn.disabled = False
        self.next_btn.text = "Next"
        self.cart_label.text = "Cart Empty"
        if hasattr(self, 'menu_layout') and self.menu_layout.parent:
            self.remove_widget(self.menu_layout)
        self.menu_layout = GridLayout(cols=2, spacing=8, size_hint_y=0.5)
    
    def check_customer(self, instance):
        name = self.name_input.text.strip()
        if not name:
            return
        self.customer_name = name
        
        if name in customers:
            info = customers[name]
            self.customer_phone = info[0]
            self.customer_address = info[1]
            self.show_menu()
        else:
            self.show_customer_details()
    
    def show_customer_details(self):
        self.name_input.disabled = True
        self.next_btn.disabled = True
        
        self.detail_layout = BoxLayout(orientation='vertical', size_hint_y=0.25, spacing=5)
        self.detail_layout.add_widget(Label(text="New Customer", font_size=16, color=(0.914, 0.271, 0.376, 1)))
        
        phone_input = TextInput(hint_text="Phone Number", multiline=False)
        self.detail_layout.add_widget(phone_input)
        
        address_input = TextInput(hint_text="Delivery Address", multiline=False)
        self.detail_layout.add_widget(address_input)
        
        def save_details(btn):
            phone = phone_input.text.strip()
            address = address_input.text.strip()
            if phone and address:
                customers[self.customer_name] = [phone, address]
                save_customers()
                self.customer_phone = phone
                self.customer_address = address
                self.remove_widget(self.detail_layout)
                self.show_menu()
        
        save_btn = Button(text="Save & Continue", size_hint_y=0.3, background_color=(0.914, 0.271, 0.376, 1))
        save_btn.bind(on_press=save_details)
        self.detail_layout.add_widget(save_btn)
        
        self.add_widget(self.detail_layout)
    
    def show_menu(self):
        if hasattr(self, 'detail_layout'):
            self.remove_widget(self.detail_layout)
        
        self.name_input.disabled = True
        self.next_btn.disabled = True
        
        self.menu_layout.clear_widgets()
        for p in products:
            btn = Button(text=f"{p['name']}\nRs.{p['price']}", font_size=12, background_color=(0.2, 0.2, 0.3, 1))
            btn.bind(on_press=lambda x, pid=p['id'], price=p['price'], name=p['name']: self.add_to_cart(pid, name, price))
            self.menu_layout.add_widget(btn)
        
        self.add_widget(self.menu_layout)
    
    def add_to_cart(self, pid, name, price):
        qty = 1
        self.cart.append({
            'name': name,
            'quantity': qty,
            'price': price,
            'subtotal': price * qty
        })
        self.update_cart_display()
    
    def update_cart_display(self):
        if not self.cart:
            self.cart_label.text = "Cart Empty"
            return
        total = sum(i['subtotal'] for i in self.cart)
        text = f"{len(self.cart)} items | Total: Rs.{total}"
        self.cart_label.text = text
    
    def finish_order(self, instance):
        if not self.cart:
            return
        total = sum(i['subtotal'] for i in self.cart)
        order_num = generate_order_number()
        
        filepath = generate_png(order_num, self.customer_name, self.customer_phone, 
                                self.customer_address, self.cart, total)
        
        orders.append({
            'order_num': order_num,
            'customer': self.customer_name,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'total': total,
            'filepath': filepath
        })
        save_orders()
        
        popup = Popup(title='Order Placed!', 
                     content=Label(text=f'Order {order_num}\nTotal: Rs.{total}\nSaved to:\n{filepath}'),
                     size_hint=(0.8, 0.4))
        popup.open()
        
        self.reset()
        Clock.schedule_once(lambda dt: setattr(self.parent, 'current', 'main'), 2)

class HistoryScreen(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
    
    def refresh(self):
        self.layout.clear_widgets()
        if not orders:
            self.layout.add_widget(Label(text="No orders yet", size_hint_y=None, height=50))
        else:
            for o in reversed(orders[-20:]):
                btn = Button(text=f"{o['order_num']} | {o['customer']} | {o['date'][:10]} | Rs.{o['total']}",
                           size_hint_y=None, height=50, background_color=(0.2, 0.2, 0.3, 1))
                self.layout.add_widget(btn)
        
        back_btn = Button(text="BACK", size_hint_y=None, height=50, background_color=(0.914, 0.271, 0.376, 1))
        back_btn.bind(on_press=lambda x: setattr(self.parent, 'current', 'main'))
        self.layout.add_widget(back_btn)

class CustomersScreen(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
    
    def refresh(self):
        self.layout.clear_widgets()
        if not customers:
            self.layout.add_widget(Label(text="No customers yet", size_hint_y=None, height=50))
        else:
            for name, (phone, address) in customers.items():
                btn = Button(text=f"{name}\nPhone: {phone}", size_hint_y=None, height=60,
                           background_color=(0.2, 0.2, 0.3, 1), font_size=12)
                self.layout.add_widget(btn)
        
        back_btn = Button(text="BACK", size_hint_y=None, height=50, background_color=(0.914, 0.271, 0.376, 1))
        back_btn.bind(on_press=lambda x: setattr(self.parent, 'current', 'main'))
        self.layout.add_widget(back_btn)

class ProductsScreen(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
    
    def refresh(self):
        self.layout.clear_widgets()
        for p in products:
            btn = Button(text=f"{p['name']} - Rs.{p['price']}", size_hint_y=None, height=50,
                       background_color=(0.2, 0.2, 0.3, 1))
            self.layout.add_widget(btn)
        
        back_btn = Button(text="BACK", size_hint_y=None, height=50, background_color=(0.914, 0.271, 0.376, 1))
        back_btn.bind(on_press=lambda x: setattr(self.parent, 'current', 'main'))
        self.layout.add_widget(back_btn)

class RazaTraderApp(App):
    def build(self):
        load_data()
        from kivy.uix.screenmanager import ScreenManager, Screen
        
        class ScreenManager(ScreenManager):
            pass
        
        class MainScreen(Screen):
            pass
        
        self.sm = ScreenManager()
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(OrderScreen(name='order'))
        self.sm.add_widget(HistoryScreen(name='history'))
        self.sm.add_widget(CustomersScreen(name='customers'))
        self.sm.add_widget(ProductsScreen(name='products'))
        return self.sm

if __name__ == '__main__':
    RazaTraderApp().run()