import os
import re
import io
import time
import json
import requests
from PIL import Image
from ddgs import DDGS

# 16 Brands x 10 Items Catalog
PRODUCTS = [
    # ---------------- APPLE (10 items) ----------------
    {
        "n": "iPhone 16 Pro 256GB", "c": "HP", "pr": 18999000, "o": 20999000, "t": "phone",
        "col": ["#8d8f94", "#d9dadd"], "b": "Apple",
        "im": ["apple-iphone-16-pro-256gb-1.jpg", "apple-iphone-16-pro-256gb-2.jpg", "apple-iphone-16-pro-256gb-3.jpg"],
        "q": "iPhone 16 Pro titanium"
    },
    {
        "n": "iPhone 16 128GB", "c": "HP", "pr": 15499000, "o": 16999000, "t": "phone",
        "col": ["#0b8073", "#82dfd3"], "b": "Apple",
        "im": ["apple-iphone-16-128gb-1.jpg"],
        "q": "iPhone 16 official product"
    },
    {
        "n": "iPhone 15 Pro 128GB", "c": "HP", "pr": 16999000, "o": 18499000, "t": "phone",
        "col": ["#474749", "#9e9ea3"], "b": "Apple",
        "im": ["apple-iphone-15-pro-128gb-1.jpg"],
        "q": "iPhone 15 Pro natural titanium"
    },
    {
        "n": "iPhone 15 128GB", "c": "HP", "pr": 11999000, "o": 12999000, "t": "phone",
        "col": ["#f1c7d4", "#ffe9ef"], "b": "Apple",
        "im": ["apple-iphone-15-128gb-1.jpg", "apple-iphone-15-128gb-2.jpg"],
        "q": "iPhone 15 official product"
    },
    {
        "n": "iPhone 14 128GB", "c": "HP", "pr": 10299000, "o": 11499000, "t": "phone",
        "col": ["#2c323f", "#6b7791"], "b": "Apple",
        "im": ["apple-iphone-14-128gb-1.jpg"],
        "q": "iPhone 14 official product"
    },
    {
        "n": "iPhone 13 128GB (Second)", "c": "HP", "pr": 6499000, "o": 7299000, "t": "phone",
        "col": ["#1b2a49", "#5d7bb8"], "b": "Apple",
        "im": ["apple-iphone-13-128gb-second-1.jpg", "apple-iphone-13-128gb-second-2.jpg", "apple-iphone-13-128gb-second-3.jpg"],
        "q": "iPhone 13 official"
    },
    {
        "n": "iPhone 12 128GB (Second)", "c": "HP", "pr": 5299000, "o": 5999000, "t": "phone",
        "col": ["#5c3c8f", "#a688d6"], "b": "Apple",
        "im": ["apple-iphone-12-128gb-1.jpg"],
        "q": "iPhone 12 official product"
    },
    {
        "n": "MacBook Air M3 13-inch 8/256", "c": "Laptop", "pr": 15999000, "o": 17499000, "t": "laptop",
        "col": ["#9aa3b2", "#dfe4ee"], "b": "Apple",
        "im": ["apple-macbook-air-m3-13-8-256-1.jpg", "apple-macbook-air-m3-13-8-256-2.jpg", "apple-macbook-air-m3-13-8-256-3.jpg"],
        "q": "MacBook Air M3 space gray"
    },
    {
        "n": "MacBook Pro 14-inch M4 16/512", "c": "Laptop", "pr": 24999000, "o": 26999000, "t": "laptop",
        "col": ["#2b2d33", "#8f95a3"], "b": "Apple",
        "im": ["apple-macbook-pro-14-inch-m4-16-512-1.jpg", "apple-macbook-pro-14-inch-m4-16-512-2.jpg", "apple-macbook-pro-14-inch-m4-16-512-3.jpg"],
        "q": "MacBook Pro 14 M4 official"
    },
    {
        "n": "AirPods Pro 2", "c": "Aksesoris", "pr": 3699000, "o": 3999000, "t": "buds",
        "col": ["#e9ebef", "#ffffff"], "b": "Apple",
        "im": ["apple-airpods-pro-2-1.jpg", "apple-airpods-pro-2-2.jpg", "apple-airpods-pro-2-3.jpg"],
        "q": "AirPods Pro 2 USB-C"
    },

    # ---------------- SAMSUNG (10 items) ----------------
    {
        "n": "Samsung Galaxy S25 256GB", "c": "HP", "pr": 13499000, "o": 14999000, "t": "phone",
        "col": ["#1c3d73", "#6aa3ff"], "b": "Samsung",
        "im": ["samsung-samsung-galaxy-s25-256gb-1.jpg", "samsung-samsung-galaxy-s25-256gb-2.jpg", "samsung-samsung-galaxy-s25-256gb-3.jpg"],
        "q": "Samsung Galaxy S25 official"
    },
    {
        "n": "Samsung Galaxy S24 Ultra 256GB", "c": "HP", "pr": 18499000, "o": 21999000, "t": "phone",
        "col": ["#363b45", "#8c94a4"], "b": "Samsung",
        "im": ["samsung-galaxy-s24-ultra-256gb-1.jpg"],
        "q": "Samsung Galaxy S24 Ultra titanium"
    },
    {
        "n": "Samsung Galaxy S24 FE 128GB", "c": "HP", "pr": 8999000, "o": 9999000, "t": "phone",
        "col": ["#2e5c8a", "#7cb8f0"], "b": "Samsung",
        "im": ["samsung-galaxy-s24-fe-128gb-1.jpg"],
        "q": "Samsung Galaxy S24 FE blue"
    },
    {
        "n": "Samsung Galaxy Z Flip6 256GB", "c": "HP", "pr": 14999000, "o": 17499000, "t": "phone",
        "col": ["#3b7d60", "#9be3be"], "b": "Samsung",
        "im": ["samsung-galaxy-z-flip6-256gb-1.jpg"],
        "q": "Samsung Galaxy Z Flip6 mint"
    },
    {
        "n": "Samsung Galaxy Z Fold6 256GB", "c": "HP", "pr": 23999000, "o": 26499000, "t": "phone",
        "col": ["#424855", "#9ca8bf"], "b": "Samsung",
        "im": ["samsung-galaxy-z-fold6-256gb-1.jpg"],
        "q": "Samsung Galaxy Z Fold6 silver shadow"
    },
    {
        "n": "Samsung Galaxy A56 5G 8/256", "c": "HP", "pr": 6799000, "o": 7399000, "t": "phone",
        "col": ["#6b4fd8", "#cdbfff"], "b": "Samsung",
        "im": ["samsung-samsung-galaxy-a56-5g-8-256-1.jpg", "samsung-samsung-galaxy-a56-5g-8-256-2.jpg", "samsung-samsung-galaxy-a56-5g-8-256-3.jpg"],
        "q": "Samsung Galaxy A56 5G"
    },
    {
        "n": "Samsung Galaxy A55 5G 8/256", "c": "HP", "pr": 5499000, "o": 5999000, "t": "phone",
        "col": ["#728099", "#c8d4eb"], "b": "Samsung",
        "im": ["samsung-galaxy-a55-5g-8-256-1.jpg"],
        "q": "Samsung Galaxy A55 5G awesome navy"
    },
    {
        "n": "Samsung Galaxy A35 5G 8/128", "c": "HP", "pr": 4399000, "o": 4999000, "t": "phone",
        "col": ["#5a718a", "#a9c4e3"], "b": "Samsung",
        "im": ["samsung-galaxy-a35-5g-8-128-1.jpg"],
        "q": "Samsung Galaxy A35 5G awesome lilac"
    },
    {
        "n": "Samsung Galaxy A16 4/128", "c": "HP", "pr": 2499000, "o": 2799000, "t": "phone",
        "col": ["#2a2f3a", "#6f7a90"], "b": "Samsung",
        "im": ["samsung-samsung-galaxy-a16-4-128-1.jpg", "samsung-samsung-galaxy-a16-4-128-2.jpg", "samsung-samsung-galaxy-a16-4-128-3.jpg"],
        "q": "Samsung Galaxy A16"
    },
    {
        "n": "Samsung Galaxy A06 4/64", "c": "HP", "pr": 1399000, "o": 1599000, "t": "phone",
        "col": ["#36445c", "#7d97c2"], "b": "Samsung",
        "im": ["samsung-galaxy-a06-4-64-1.jpg"],
        "q": "Samsung Galaxy A06 blue"
    },

    # ---------------- XIAOMI (10 items) ----------------
    {
        "n": "Xiaomi 14T Pro 12/512", "c": "HP", "pr": 8999000, "o": 9999000, "t": "phone",
        "col": ["#222a36", "#6f8cb5"], "b": "Xiaomi",
        "im": ["xiaomi-14t-pro-12-512-1.jpg"],
        "q": "Xiaomi 14T Pro titan gray"
    },
    {
        "n": "Xiaomi 14T 8/256", "c": "HP", "pr": 7999000, "o": 8799000, "t": "phone",
        "col": ["#0f5e8c", "#7fd0ff"], "b": "Xiaomi",
        "im": ["xiaomi-xiaomi-14t-8-256-1.jpg", "xiaomi-xiaomi-14t-8-256-2.jpg", "xiaomi-xiaomi-14t-8-256-3.jpg"],
        "q": "Xiaomi 14T"
    },
    {
        "n": "Xiaomi 14 12/512", "c": "HP", "pr": 10999000, "o": 12499000, "t": "phone",
        "col": ["#1e3b2b", "#62b082"], "b": "Xiaomi",
        "im": ["xiaomi-14-12-512-1.jpg"],
        "q": "Xiaomi 14 green leica"
    },
    {
        "n": "Xiaomi 13T 12/256", "c": "HP", "pr": 5799000, "o": 6499000, "t": "phone",
        "col": ["#204060", "#6ca5e0"], "b": "Xiaomi",
        "im": ["xiaomi-13t-12-256-1.jpg"],
        "q": "Xiaomi 13T alpine blue"
    },
    {
        "n": "Xiaomi Redmi Note 14 Pro+ 5G", "c": "HP", "pr": 4899000, "o": 5499000, "t": "phone",
        "col": ["#3b2857", "#9872d4"], "b": "Xiaomi",
        "im": ["xiaomi-redmi-note-14-pro-plus-1.jpg"],
        "q": "Redmi Note 14 Pro Plus 5G"
    },
    {
        "n": "Xiaomi Redmi Note 14 8/256", "c": "HP", "pr": 3299000, "o": 3699000, "t": "phone",
        "col": ["#2d2d2f", "#8e44ff"], "b": "Xiaomi",
        "im": ["xiaomi-xiaomi-redmi-note-14-8-256-1.jpg", "xiaomi-xiaomi-redmi-note-14-8-256-2.jpg", "xiaomi-xiaomi-redmi-note-14-8-256-3.jpg"],
        "q": "Redmi Note 14"
    },
    {
        "n": "Xiaomi Redmi Note 13 Pro 8/256", "c": "HP", "pr": 3499000, "o": 3999000, "t": "phone",
        "col": ["#234b6b", "#70b2e8"], "b": "Xiaomi",
        "im": ["xiaomi-redmi-note-13-pro-1.jpg"],
        "q": "Redmi Note 13 Pro 4G official"
    },
    {
        "n": "Xiaomi Redmi Note 13 8/256", "c": "HP", "pr": 2499000, "o": 2799000, "t": "phone",
        "col": ["#385a4a", "#78c29e"], "b": "Xiaomi",
        "im": ["xiaomi-redmi-note-13-1.jpg"],
        "q": "Redmi Note 13 mint green"
    },
    {
        "n": "Xiaomi Redmi 14C 6/128", "c": "HP", "pr": 1499000, "o": 1699000, "t": "phone",
        "col": ["#223a54", "#669bd4"], "b": "Xiaomi",
        "im": ["xiaomi-redmi-14c-1.jpg"],
        "q": "Redmi 14C starry blue"
    },
    {
        "n": "Xiaomi Redmi 13 8/128", "c": "HP", "pr": 1799000, "o": 1999000, "t": "phone",
        "col": ["#5a3d75", "#ba92e3"], "b": "Xiaomi",
        "im": ["xiaomi-redmi-13-1.jpg"],
        "q": "Redmi 13 sandy gold"
    },

    # ---------------- OPPO (10 items) ----------------
    {
        "n": "OPPO Find X8 Pro 16/512", "c": "HP", "pr": 18499000, "o": 19999000, "t": "phone",
        "col": ["#1c2938", "#6a8fb8"], "b": "OPPO",
        "im": ["oppo-find-x8-pro-1.jpg"],
        "q": "OPPO Find X8 Pro space black"
    },
    {
        "n": "OPPO Find X8 12/256", "c": "HP", "pr": 13999000, "o": 14999000, "t": "phone",
        "col": ["#758499", "#d0dded"], "b": "OPPO",
        "im": ["oppo-find-x8-1.jpg"],
        "q": "OPPO Find X8 star grey"
    },
    {
        "n": "OPPO Reno13 5G 12/256", "c": "HP", "pr": 7299000, "o": 7999000, "t": "phone",
        "col": ["#0e7c86", "#7fe0c8"], "b": "OPPO",
        "im": ["oppo-oppo-reno13-5g-12-256-1.jpg", "oppo-oppo-reno13-5g-12-256-2.jpg", "oppo-oppo-reno13-5g-12-256-3.jpg"],
        "q": "OPPO Reno13 5G"
    },
    {
        "n": "OPPO Reno12 Pro 5G 12/512", "c": "HP", "pr": 7999000, "o": 8999000, "t": "phone",
        "col": ["#6b4938", "#d1a890"], "b": "OPPO",
        "im": ["oppo-reno12-pro-5g-1.jpg"],
        "q": "OPPO Reno12 Pro 5G sunset gold"
    },
    {
        "n": "OPPO Reno12 5G 12/256", "c": "HP", "pr": 5999000, "o": 6699000, "t": "phone",
        "col": ["#5a4f78", "#bfaee3"], "b": "OPPO",
        "im": ["oppo-reno12-5g-1.jpg"],
        "q": "OPPO Reno12 5G astro silver"
    },
    {
        "n": "OPPO Reno11 F 5G 8/256", "c": "HP", "pr": 3999000, "o": 4499000, "t": "phone",
        "col": ["#1a5247", "#5cd6be"], "b": "OPPO",
        "im": ["oppo-reno11-f-5g-1.jpg"],
        "q": "OPPO Reno11 F 5G palm green"
    },
    {
        "n": "OPPO A5 Pro 8/256", "c": "HP", "pr": 3199000, "o": 3499000, "t": "phone",
        "col": ["#7a3fb0", "#e4c6ff"], "b": "OPPO",
        "im": ["oppo-oppo-a5-pro-8-256-1.jpg", "oppo-oppo-a5-pro-8-256-2.jpg", "oppo-oppo-a5-pro-8-256-3.jpg"],
        "q": "OPPO A5 Pro"
    },
    {
        "n": "OPPO A79 5G 8/256", "c": "HP", "pr": 3299000, "o": 3799000, "t": "phone",
        "col": ["#42325c", "#987bcf"], "b": "OPPO",
        "im": ["oppo-a79-5g-1.jpg"],
        "q": "OPPO A79 5G purple"
    },
    {
        "n": "OPPO A60 8/128", "c": "HP", "pr": 2299000, "o": 2599000, "t": "phone",
        "col": ["#1e4659", "#63afcf"], "b": "OPPO",
        "im": ["oppo-a60-1.jpg"],
        "q": "OPPO A60 ripple blue"
    },
    {
        "n": "OPPO A38 4/128", "c": "HP", "pr": 1699000, "o": 1899000, "t": "phone",
        "col": ["#5c4a22", "#d9b666"], "b": "OPPO",
        "im": ["oppo-a38-1.jpg"],
        "q": "OPPO A38 glowing gold"
    },

    # ---------------- VIVO (10 items) ----------------
    {
        "n": "vivo X200 Pro 16/512", "c": "HP", "pr": 16999000, "o": 18499000, "t": "phone",
        "col": ["#1f2d3d", "#648ab3"], "b": "vivo",
        "im": ["vivo-x200-pro-1.jpg"],
        "q": "vivo X200 Pro zeiss"
    },
    {
        "n": "vivo X200 12/256", "c": "HP", "pr": 12999000, "o": 13999000, "t": "phone",
        "col": ["#3b5266", "#87b0d4"], "b": "vivo",
        "im": ["vivo-x200-1.jpg"],
        "q": "vivo X200 official"
    },
    {
        "n": "vivo V50 12/512", "c": "HP", "pr": 7999000, "o": 8499000, "t": "phone",
        "col": ["#b5446e", "#ffc2d6"], "b": "vivo",
        "im": ["vivo-vivo-v50-12-512-1.jpg", "vivo-vivo-v50-12-512-2.jpg", "vivo-vivo-v50-12-512-3.jpg"],
        "q": "vivo V50"
    },
    {
        "n": "vivo V40 5G 12/256", "c": "HP", "pr": 6499000, "o": 6999000, "t": "phone",
        "col": ["#6b425b", "#d99ec0"], "b": "vivo",
        "im": ["vivo-v40-5g-1.jpg"],
        "q": "vivo V40 5G peach"
    },
    {
        "n": "vivo V40 Lite 5G 8/256", "c": "HP", "pr": 4299000, "o": 4799000, "t": "phone",
        "col": ["#54386b", "#bb93db"], "b": "vivo",
        "im": ["vivo-v40-lite-5g-1.jpg"],
        "q": "vivo V40 Lite 5G titanium"
    },
    {
        "n": "vivo V30 5G 8/256", "c": "HP", "pr": 4999000, "o": 5499000, "t": "phone",
        "col": ["#1f4740", "#63bfb0"], "b": "vivo",
        "im": ["vivo-v30-5g-1.jpg"],
        "q": "vivo V30 5G green"
    },
    {
        "n": "vivo Y29 8/256", "c": "HP", "pr": 2799000, "o": 3099000, "t": "phone",
        "col": ["#0e8a6a", "#9ef0cf"], "b": "vivo",
        "im": ["vivo-vivo-y29-8-256-1.jpg", "vivo-vivo-y29-8-256-2.jpg", "vivo-vivo-y29-8-256-3.jpg"],
        "q": "vivo Y29"
    },
    {
        "n": "vivo Y28 8/128", "c": "HP", "pr": 2199000, "o": 2499000, "t": "phone",
        "col": ["#423a2a", "#baab89"], "b": "vivo",
        "im": ["vivo-y28-1.jpg"],
        "q": "vivo Y28 orange glitter"
    },
    {
        "n": "vivo Y18 4/64", "c": "HP", "pr": 1499000, "o": 1699000, "t": "phone",
        "col": ["#1f3b4d", "#64a4cc"], "b": "vivo",
        "im": ["vivo-y18-1.jpg"],
        "q": "vivo Y18 wave green"
    },
    {
        "n": "vivo Y03 4/64", "c": "HP", "pr": 1199000, "o": 1399000, "t": "phone",
        "col": ["#2b4232", "#75ad85"], "b": "vivo",
        "im": ["vivo-y03-1.jpg"],
        "q": "vivo Y03 green"
    },

    # ---------------- REALME (10 items) ----------------
    {
        "n": "realme GT 6 16/512", "c": "HP", "pr": 7499000, "o": 7999000, "t": "phone",
        "col": ["#244b42", "#66c4af"], "b": "realme",
        "im": ["realme-gt-6-1.jpg"],
        "q": "realme GT 6 fluid silver"
    },
    {
        "n": "realme 14 Pro+ 12/256", "c": "HP", "pr": 6499000, "o": 6999000, "t": "phone",
        "col": ["#e0a82e", "#fff0b3"], "b": "realme",
        "im": ["realme-realme-14-pro-12-256-1.jpg", "realme-realme-14-pro-12-256-2.jpg", "realme-realme-14-pro-12-256-3.jpg"],
        "q": "realme 14 Pro Plus"
    },
    {
        "n": "realme 13 Pro+ 5G 12/512", "c": "HP", "pr": 5999000, "o": 6499000, "t": "phone",
        "col": ["#3b5247", "#8ac7ad"], "b": "realme",
        "im": ["realme-13-pro-plus-1.jpg"],
        "q": "realme 13 Pro Plus monet gold"
    },
    {
        "n": "realme 13 8/128", "c": "HP", "pr": 2799000, "o": 2999000, "t": "phone",
        "col": ["#2e4759", "#72a7cc"], "b": "realme",
        "im": ["realme-13-1.jpg"],
        "q": "realme 13 pioneer green"
    },
    {
        "n": "realme 12+ 5G 8/256", "c": "HP", "pr": 3699000, "o": 4199000, "t": "phone",
        "col": ["#1f4035", "#5eb096"], "b": "realme",
        "im": ["realme-12-plus-5g-1.jpg"],
        "q": "realme 12 Plus 5G pioneer green"
    },
    {
        "n": "realme 12 5G 8/256", "c": "HP", "pr": 3199000, "o": 3599000, "t": "phone",
        "col": ["#54452a", "#c4a878"], "b": "realme",
        "im": ["realme-12-5g-1.jpg"],
        "q": "realme 12 5G twilight purple"
    },
    {
        "n": "realme C75 8/256", "c": "HP", "pr": 2899000, "o": 3199000, "t": "phone",
        "col": ["#d6a21c", "#fff3c4"], "b": "realme",
        "im": ["realme-realme-c75-8-256-1.jpg", "realme-realme-c75-8-256-2.jpg", "realme-realme-c75-8-256-3.jpg"],
        "q": "realme C75"
    },
    {
        "n": "realme C67 8/128", "c": "HP", "pr": 2199000, "o": 2499000, "t": "phone",
        "col": ["#2a4d38", "#6ebd8e"], "b": "realme",
        "im": ["realme-c67-1.jpg"],
        "q": "realme C67 sunny oasis"
    },
    {
        "n": "realme C65 8/128", "c": "HP", "pr": 1999000, "o": 2299000, "t": "phone",
        "col": ["#573d6b", "#b994d6"], "b": "realme",
        "im": ["realme-c65-1.jpg"],
        "q": "realme C65 starlight purple"
    },
    {
        "n": "realme Note 60 4/64", "c": "HP", "pr": 1299000, "o": 1499000, "t": "phone",
        "col": ["#203b54", "#5c94c7"], "b": "realme",
        "im": ["realme-note-60-1.jpg"],
        "q": "realme Note 60 marble black"
    },

    # ---------------- GOOGLE (10 items) ----------------
    {
        "n": "Google Pixel 9 Pro XL 16/256", "c": "HP", "pr": 17999000, "o": 19999000, "t": "phone",
        "col": ["#222a33", "#748ca6"], "b": "Google",
        "im": ["google-pixel-9-pro-xl-1.jpg"],
        "q": "Google Pixel 9 Pro XL obsidian"
    },
    {
        "n": "Google Pixel 9 Pro 16/128", "c": "HP", "pr": 14999000, "o": 16499000, "t": "phone",
        "col": ["#6e706e", "#d2d4d2"], "b": "Google",
        "im": ["google-pixel-9-pro-1.jpg"],
        "q": "Google Pixel 9 Pro porcelain"
    },
    {
        "n": "Google Pixel 9 12/256", "c": "HP", "pr": 11499000, "o": 12499000, "t": "phone",
        "col": ["#3b3f46", "#c9ced8"], "b": "Google",
        "im": ["google-google-pixel-9-12-256-1.jpg", "google-google-pixel-9-12-256-2.jpg", "google-google-pixel-9-12-256-3.jpg"],
        "q": "Google Pixel 9"
    },
    {
        "n": "Google Pixel 8 Pro 12/128", "c": "HP", "pr": 10999000, "o": 12499000, "t": "phone",
        "col": ["#224763", "#6daade"], "b": "Google",
        "im": ["google-pixel-8-pro-1.jpg"],
        "q": "Google Pixel 8 Pro bay blue"
    },
    {
        "n": "Google Pixel 8 8/128", "c": "HP", "pr": 8499000, "o": 9499000, "t": "phone",
        "col": ["#6b4946", "#d49b96"], "b": "Google",
        "im": ["google-pixel-8-1.jpg"],
        "q": "Google Pixel 8 rose"
    },
    {
        "n": "Google Pixel 8a 8/128", "c": "HP", "pr": 6999000, "o": 7799000, "t": "phone",
        "col": ["#1f5761", "#61bfd1"], "b": "Google",
        "im": ["google-pixel-8a-1.jpg"],
        "q": "Google Pixel 8a bay"
    },
    {
        "n": "Google Pixel 7 Pro 12/128", "c": "HP", "pr": 6999000, "o": 7999000, "t": "phone",
        "col": ["#424d45", "#94a89a"], "b": "Google",
        "im": ["google-pixel-7-pro-1.jpg"],
        "q": "Google Pixel 7 Pro hazel"
    },
    {
        "n": "Google Pixel 7 8/128", "c": "HP", "pr": 5299000, "o": 5999000, "t": "phone",
        "col": ["#616347", "#c4c79d"], "b": "Google",
        "im": ["google-pixel-7-1.jpg"],
        "q": "Google Pixel 7 lemongrass"
    },
    {
        "n": "Google Pixel 7a 8/128", "c": "HP", "pr": 4799000, "o": 5299000, "t": "phone",
        "col": ["#294863", "#74a8d4"], "b": "Google",
        "im": ["google-pixel-7a-1.jpg"],
        "q": "Google Pixel 7a sea"
    },
    {
        "n": "Google Pixel 6a 6/128", "c": "HP", "pr": 3699000, "o": 4199000, "t": "phone",
        "col": ["#36473b", "#7fa187"], "b": "Google",
        "im": ["google-pixel-6a-1.jpg"],
        "q": "Google Pixel 6a sage"
    },

    # ---------------- POCO (10 items) ----------------
    {
        "n": "POCO F6 Pro 12/512", "c": "HP", "pr": 7999000, "o": 8799000, "t": "phone",
        "col": ["#242426", "#87878c"], "b": "POCO",
        "im": ["poco-f6-pro-1.jpg"],
        "q": "POCO F6 Pro black"
    },
    {
        "n": "POCO F6 8/256", "c": "HP", "pr": 5299000, "o": 5799000, "t": "phone",
        "col": ["#224238", "#61ab95"], "b": "POCO",
        "im": ["poco-f6-1.jpg"],
        "q": "POCO F6 green"
    },
    {
        "n": "POCO X7 Pro 8/256", "c": "HP", "pr": 4999000, "o": 5499000, "t": "phone",
        "col": ["#e6c200", "#222"], "b": "POCO",
        "im": ["poco-poco-x7-pro-8-256-1.jpg", "poco-poco-x7-pro-8-256-2.jpg", "poco-poco-x7-pro-8-256-3.jpg"],
        "q": "POCO X7 Pro"
    },
    {
        "n": "POCO X6 Pro 5G 12/512", "c": "HP", "pr": 4499000, "o": 4999000, "t": "phone",
        "col": ["#f5b800", "#303030"], "b": "POCO",
        "im": ["poco-x6-pro-1.jpg"],
        "q": "POCO X6 Pro yellow"
    },
    {
        "n": "POCO X6 5G 8/256", "c": "HP", "pr": 3499000, "o": 3999000, "t": "phone",
        "col": ["#1f3f61", "#629bd4"], "b": "POCO",
        "im": ["poco-x6-1.jpg"],
        "q": "POCO X6 5G blue"
    },
    {
        "n": "POCO M6 Pro 8/256", "c": "HP", "pr": 2799000, "o": 2999000, "t": "phone",
        "col": ["#3f3557", "#9884c7"], "b": "POCO",
        "im": ["poco-m6-pro-1.jpg"],
        "q": "POCO M6 Pro purple"
    },
    {
        "n": "POCO M6 8/256", "c": "HP", "pr": 1899000, "o": 2099000, "t": "phone",
        "col": ["#57476e", "#b699de"], "b": "POCO",
        "im": ["poco-m6-1.jpg"],
        "q": "POCO M6 purple"
    },
    {
        "n": "POCO C65 6/128", "c": "HP", "pr": 1399000, "o": 1599000, "t": "phone",
        "col": ["#5c3d49", "#ba869b"], "b": "POCO",
        "im": ["poco-c65-1.jpg"],
        "q": "POCO C65 purple"
    },
    {
        "n": "POCO C75 6/128", "c": "HP", "pr": 1499000, "o": 1699000, "t": "phone",
        "col": ["#1f4038", "#62b39f"], "b": "POCO",
        "im": ["poco-c75-1.jpg"],
        "q": "POCO C75 green"
    },
    {
        "n": "POCO F5 5G 8/256", "c": "HP", "pr": 4299000, "o": 4799000, "t": "phone",
        "col": ["#204757", "#6bb5d4"], "b": "POCO",
        "im": ["poco-f5-1.jpg"],
        "q": "POCO F5 blue"
    },

    # ---------------- ASUS (10 items) ----------------
    {
        "n": "ASUS ROG Strix G16 RTX 4060", "c": "Laptop", "pr": 24499000, "o": 26499000, "t": "laptop",
        "col": ["#1a1a1a", "#ff2e4d"], "b": "ASUS",
        "im": ["asus-asus-rog-strix-g16-rtx-4060-1.jpg", "asus-asus-rog-strix-g16-rtx-4060-2.jpg", "asus-asus-rog-strix-g16-rtx-4060-3.jpg"],
        "q": "ASUS ROG Strix G16"
    },
    {
        "n": "ASUS ROG Zephyrus G14 RTX 4060", "c": "Laptop", "pr": 29999000, "o": 32999000, "t": "laptop",
        "col": ["#7d8085", "#dedede"], "b": "ASUS",
        "im": ["asus-rog-zephyrus-g14-1.jpg"],
        "q": "ASUS ROG Zephyrus G14 white"
    },
    {
        "n": "ASUS TUF Gaming A15 Ryzen 7", "c": "Laptop", "pr": 16499000, "o": 17999000, "t": "laptop",
        "col": ["#262626", "#e08b28"], "b": "ASUS",
        "im": ["asus-tuf-gaming-a15-1.jpg"],
        "q": "ASUS TUF Gaming A15 mecha gray"
    },
    {
        "n": "ASUS TUF Gaming F15 Core i5", "c": "Laptop", "pr": 12499000, "o": 13999000, "t": "laptop",
        "col": ["#242930", "#738b9e"], "b": "ASUS",
        "im": ["asus-tuf-gaming-f15-1.jpg"],
        "q": "ASUS TUF Gaming F15"
    },
    {
        "n": "ASUS Zenbook 14 OLED Ultra 5", "c": "Laptop", "pr": 14999000, "o": 16299000, "t": "laptop",
        "col": ["#1c4d6b", "#9fd6f0"], "b": "ASUS",
        "im": ["asus-asus-zenbook-14-oled-ultra-5-1.jpg", "asus-asus-zenbook-14-oled-ultra-5-2.jpg", "asus-asus-zenbook-14-oled-ultra-5-3.jpg"],
        "q": "ASUS Zenbook 14 OLED"
    },
    {
        "n": "ASUS Zenbook 14 OLED Ultra 7", "c": "Laptop", "pr": 18499000, "o": 19999000, "t": "laptop",
        "col": ["#1f364a", "#78aed9"], "b": "ASUS",
        "im": ["asus-zenbook-14-oled-ultra-7-1.jpg"],
        "q": "ASUS Zenbook 14 OLED ponder blue"
    },
    {
        "n": "ASUS Vivobook 14 Core i5", "c": "Laptop", "pr": 8499000, "o": 9299000, "t": "laptop",
        "col": ["#2b6cb0", "#9cc7ff"], "b": "ASUS",
        "im": ["asus-asus-vivobook-14-core-i5-1.jpg", "asus-asus-vivobook-14-core-i5-2.jpg", "asus-asus-vivobook-14-core-i5-3.jpg"],
        "q": "ASUS Vivobook 14"
    },
    {
        "n": "ASUS Vivobook 15 Core i3", "c": "Laptop", "pr": 6299000, "o": 6799000, "t": "laptop",
        "col": ["#38424d", "#8c9fb3"], "b": "ASUS",
        "im": ["asus-vivobook-15-1.jpg"],
        "q": "ASUS Vivobook 15 quiet blue"
    },
    {
        "n": "ASUS Vivobook Go 14 Ryzen 3", "c": "Laptop", "pr": 5799000, "o": 6299000, "t": "laptop",
        "col": ["#2b3847", "#718ca8"], "b": "ASUS",
        "im": ["asus-vivobook-go-14-1.jpg"],
        "q": "ASUS Vivobook Go 14 mixed black"
    },
    {
        "n": "ASUS ROG Ally Z1 Extreme", "c": "Laptop", "pr": 9999000, "o": 11299000, "t": "laptop",
        "col": ["#e0e4eb", "#ffffff"], "b": "ASUS",
        "im": ["asus-rog-ally-z1-extreme-1.jpg"],
        "q": "ASUS ROG Ally handheld"
    },

    # ---------------- LENOVO (10 items) ----------------
    {
        "n": "Lenovo Legion Pro 5 RTX 4070", "c": "Laptop", "pr": 26999000, "o": 29999000, "t": "laptop",
        "col": ["#202329", "#566782"], "b": "Lenovo",
        "im": ["lenovo-legion-pro-5-1.jpg"],
        "q": "Lenovo Legion Pro 5 onyx grey"
    },
    {
        "n": "Lenovo Legion Slim 5 Ryzen 7", "c": "Laptop", "pr": 20499000, "o": 22499000, "t": "laptop",
        "col": ["#2c2f36", "#6c778c"], "b": "Lenovo",
        "im": ["lenovo-legion-slim-5-1.jpg"],
        "q": "Lenovo Legion Slim 5 storm grey"
    },
    {
        "n": "Lenovo LOQ 15 RTX 3050", "c": "Laptop", "pr": 13999000, "o": 14999000, "t": "laptop",
        "col": ["#2a2f45", "#7b6cff"], "b": "Lenovo",
        "im": ["lenovo-lenovo-loq-15-rtx-3050-1.jpg", "lenovo-lenovo-loq-15-rtx-3050-2.jpg", "lenovo-lenovo-loq-15-rtx-3050-3.jpg"],
        "q": "Lenovo LOQ 15"
    },
    {
        "n": "Lenovo LOQ 15 RTX 4050", "c": "Laptop", "pr": 16499000, "o": 17999000, "t": "laptop",
        "col": ["#242c38", "#6684ad"], "b": "Lenovo",
        "im": ["lenovo-loq-15-rtx-4050-1.jpg"],
        "q": "Lenovo LOQ 15 luna grey"
    },
    {
        "n": "Lenovo Yoga Slim 7 Intel Ultra", "c": "Laptop", "pr": 17499000, "o": 18999000, "t": "laptop",
        "col": ["#203847", "#649cb8"], "b": "Lenovo",
        "im": ["lenovo-yoga-slim-7-1.jpg"],
        "q": "Lenovo Yoga Slim 7 tidal teal"
    },
    {
        "n": "Lenovo IdeaPad Slim 5 Ryzen 7", "c": "Laptop", "pr": 11499000, "o": 12499000, "t": "laptop",
        "col": ["#363c45", "#8c98a8"], "b": "Lenovo",
        "im": ["lenovo-ideapad-slim-5-1.jpg"],
        "q": "Lenovo IdeaPad Slim 5 cloud grey"
    },
    {
        "n": "Lenovo IdeaPad Slim 3 Ryzen 5", "c": "Laptop", "pr": 7299000, "o": 7899000, "t": "laptop",
        "col": ["#3a3f4b", "#a9b2c3"], "b": "Lenovo",
        "im": ["lenovo-lenovo-ideapad-slim-3-ryzen-5-1.jpg", "lenovo-lenovo-ideapad-slim-3-ryzen-5-2.jpg", "lenovo-lenovo-ideapad-slim-3-ryzen-5-3.jpg"],
        "q": "Lenovo IdeaPad Slim 3"
    },
    {
        "n": "Lenovo IdeaPad Slim 3 Core i3", "c": "Laptop", "pr": 6199000, "o": 6699000, "t": "laptop",
        "col": ["#3b424d", "#7c8b9e"], "b": "Lenovo",
        "im": ["lenovo-ideapad-slim-3-i3-1.jpg"],
        "q": "Lenovo IdeaPad Slim 3 arctic grey"
    },
    {
        "n": "Lenovo IdeaPad 1 Celeron N4020", "c": "Laptop", "pr": 3999000, "o": 4499000, "t": "laptop",
        "col": ["#424854", "#8c96a6"], "b": "Lenovo",
        "im": ["lenovo-ideapad-1-1.jpg"],
        "q": "Lenovo IdeaPad 1 platinum grey"
    },
    {
        "n": "Lenovo ThinkPad E14 Core i5", "c": "Laptop", "pr": 12499000, "o": 13999000, "t": "laptop",
        "col": ["#14161a", "#4a4f5c"], "b": "Lenovo",
        "im": ["lenovo-thinkpad-e14-1.jpg"],
        "q": "Lenovo ThinkPad E14 black"
    },

    # ---------------- ACER (10 items) ----------------
    {
        "n": "Acer Predator Helios Neo 16 RTX 4060", "c": "Laptop", "pr": 21999000, "o": 23999000, "t": "laptop",
        "col": ["#1c2026", "#00d0ff"], "b": "Acer",
        "im": ["acer-predator-helios-neo-16-1.jpg"],
        "q": "Acer Predator Helios Neo 16"
    },
    {
        "n": "Acer Nitro V 15 RTX 4050", "c": "Laptop", "pr": 14299000, "o": 15499000, "t": "laptop",
        "col": ["#1a1f29", "#247ee0"], "b": "Acer",
        "im": ["acer-nitro-v-15-rtx-4050-1.jpg"],
        "q": "Acer Nitro V 15 black"
    },
    {
        "n": "Acer Nitro V 15 RTX 2050", "c": "Laptop", "pr": 10999000, "o": 11999000, "t": "laptop",
        "col": ["#202630", "#386596"], "b": "Acer",
        "im": ["acer-nitro-v-15-rtx-2050-1.jpg"],
        "q": "Acer Nitro V 15"
    },
    {
        "n": "Acer Swift Go 14 OLED Core i5", "c": "Laptop", "pr": 12499000, "o": 13499000, "t": "laptop",
        "col": ["#7a8a99", "#d9e3ee"], "b": "Acer",
        "im": ["acer-acer-swift-go-14-oled-core-i5-1.jpg", "acer-acer-swift-go-14-oled-core-i5-2.jpg", "acer-acer-swift-go-14-oled-core-i5-3.jpg"],
        "q": "Acer Swift Go 14 OLED"
    },
    {
        "n": "Acer Swift Go 14 OLED Core i7", "c": "Laptop", "pr": 15999000, "o": 17299000, "t": "laptop",
        "col": ["#5a6e80", "#b2c8de"], "b": "Acer",
        "im": ["acer-swift-go-14-oled-i7-1.jpg"],
        "q": "Acer Swift Go 14 OLED silver"
    },
    {
        "n": "Acer Aspire 5 Core i7", "c": "Laptop", "pr": 10999000, "o": 11999000, "t": "laptop",
        "col": ["#2f7d5b", "#a8e6c8"], "b": "Acer",
        "im": ["acer-acer-aspire-5-core-i7-1.jpg", "acer-acer-aspire-5-core-i7-2.jpg", "acer-acer-aspire-5-core-i7-3.jpg"],
        "q": "Acer Aspire 5 Core i7"
    },
    {
        "n": "Acer Aspire 5 Core i5", "c": "Laptop", "pr": 8699000, "o": 9499000, "t": "laptop",
        "col": ["#2b4a54", "#6bb5c9"], "b": "Acer",
        "im": ["acer-aspire-5-i5-1.jpg"],
        "q": "Acer Aspire 5 steel gray"
    },
    {
        "n": "Acer Aspire 3 Ryzen 5", "c": "Laptop", "pr": 6999000, "o": 7599000, "t": "laptop",
        "col": ["#3b4752", "#879cb0"], "b": "Acer",
        "im": ["acer-aspire-3-ryzen-5-1.jpg"],
        "q": "Acer Aspire 3 pure silver"
    },
    {
        "n": "Acer Aspire 3 Core i3", "c": "Laptop", "pr": 5699000, "o": 6199000, "t": "laptop",
        "col": ["#363c45", "#7e8a9c"], "b": "Acer",
        "im": ["acer-aspire-3-i3-1.jpg"],
        "q": "Acer Aspire 3 silver"
    },
    {
        "n": "Acer Aspire Lite Core i3", "c": "Laptop", "pr": 4999000, "o": 5499000, "t": "laptop",
        "col": ["#333e4a", "#6f849c"], "b": "Acer",
        "im": ["acer-aspire-lite-i3-1.jpg"],
        "q": "Acer Aspire Lite titanium gray"
    },

    # ---------------- HP (10 items) ----------------
    {
        "n": "HP OMEN 16 Core i7 RTX 4060", "c": "Laptop", "pr": 23999000, "o": 26499000, "t": "laptop",
        "col": ["#1c1c1f", "#e63946"], "b": "HP",
        "im": ["hp-omen-16-1.jpg"],
        "q": "HP OMEN 16 shadow black"
    },
    {
        "n": "HP Victus 16 Core i5 RTX 4050", "c": "Laptop", "pr": 15499000, "o": 16999000, "t": "laptop",
        "col": ["#222a33", "#4382bf"], "b": "HP",
        "im": ["hp-victus-16-1.jpg"],
        "q": "HP Victus 16 mica silver"
    },
    {
        "n": "HP Victus 15 Ryzen 5 RTX 2050", "c": "Laptop", "pr": 10499000, "o": 11499000, "t": "laptop",
        "col": ["#232830", "#54687d"], "b": "HP",
        "im": ["hp-victus-15-1.jpg"],
        "q": "HP Victus 15 performance blue"
    },
    {
        "n": "HP Envy x360 2-in-1 Core i5", "c": "Laptop", "pr": 15999000, "o": 17299000, "t": "laptop",
        "col": ["#5a6575", "#b8c7db"], "b": "HP",
        "im": ["hp-envy-x360-i5-1.jpg"],
        "q": "HP Envy x360 2 in 1 natural silver"
    },
    {
        "n": "HP Envy x360 2-in-1 Ryzen 7", "c": "Laptop", "pr": 17499000, "o": 18999000, "t": "laptop",
        "col": ["#232b36", "#6f88a8"], "b": "HP",
        "im": ["hp-envy-x360-ryzen-7-1.jpg"],
        "q": "HP Envy x360 nightfall black"
    },
    {
        "n": "HP Pavilion 14 Core i5 16/512", "c": "Laptop", "pr": 9299000, "o": 9999000, "t": "laptop",
        "col": ["#c9d3e3", "#eef2fa"], "b": "HP",
        "im": ["hp-hp-pavilion-14-core-i5-16-512-1.jpg", "hp-hp-pavilion-14-core-i5-16-512-2.jpg", "hp-hp-pavilion-14-core-i5-16-512-3.jpg"],
        "q": "HP Pavilion 14"
    },
    {
        "n": "HP Pavilion Plus 14 OLED Core i7", "c": "Laptop", "pr": 16999000, "o": 18499000, "t": "laptop",
        "col": ["#253545", "#7aa5cc"], "b": "HP",
        "im": ["hp-pavilion-plus-14-1.jpg"],
        "q": "HP Pavilion Plus 14 OLED space blue"
    },
    {
        "n": "HP 14s Core i5 8/512", "c": "Laptop", "pr": 8299000, "o": 8999000, "t": "laptop",
        "col": ["#3d4752", "#90a2b5"], "b": "HP",
        "im": ["hp-14s-i5-1.jpg"],
        "q": "HP 14s natural silver"
    },
    {
        "n": "HP 14s Core i3 8/512", "c": "Laptop", "pr": 6199000, "o": 6799000, "t": "laptop",
        "col": ["#363e47", "#8493a3"], "b": "HP",
        "im": ["hp-14s-i3-1.jpg"],
        "q": "HP 14s silver"
    },
    {
        "n": "HP 15s Ryzen 5 8/512", "c": "Laptop", "pr": 7499000, "o": 8199000, "t": "laptop",
        "col": ["#2e3d4a", "#698aa6"], "b": "HP",
        "im": ["hp-15s-ryzen-5-1.jpg"],
        "q": "HP 15s warm gold"
    },

    # ---------------- DELL (10 items) ----------------
    {
        "n": "Dell Alienware m16 RTX 4070", "c": "Laptop", "pr": 32999000, "o": 36999000, "t": "laptop",
        "col": ["#1a1d24", "#00e1d9"], "b": "Dell",
        "im": ["dell-alienware-m16-1.jpg"],
        "q": "Dell Alienware m16 dark metallic"
    },
    {
        "n": "Dell G15 Gaming Core i7 RTX 4060", "c": "Laptop", "pr": 19499000, "o": 21999000, "t": "laptop",
        "col": ["#262a30", "#d14b4b"], "b": "Dell",
        "im": ["dell-g15-rtx-4060-1.jpg"],
        "q": "Dell G15 5530 quantum white"
    },
    {
        "n": "Dell G15 Gaming RTX 3050", "c": "Laptop", "pr": 13999000, "o": 15499000, "t": "laptop",
        "col": ["#232830", "#ff6b35"], "b": "Dell",
        "im": ["dell-g15-rtx-3050-1.jpg"],
        "q": "Dell G15 dark shadow gray"
    },
    {
        "n": "Dell XPS 13 Core Ultra 7", "c": "Laptop", "pr": 25999000, "o": 28999000, "t": "laptop",
        "col": ["#42464f", "#b4bac4"], "b": "Dell",
        "im": ["dell-xps-13-1.jpg"],
        "q": "Dell XPS 13 platinum silver"
    },
    {
        "n": "Dell XPS 14 Core Ultra 7", "c": "Laptop", "pr": 31999000, "o": 34999000, "t": "laptop",
        "col": ["#2b2f36", "#8792a1"], "b": "Dell",
        "im": ["dell-xps-14-1.jpg"],
        "q": "Dell XPS 14 graphite"
    },
    {
        "n": "Dell Inspiron 15 Core i5 8/512", "c": "Laptop", "pr": 9999000, "o": 10799000, "t": "laptop",
        "col": ["#222a3a", "#7d8cab"], "b": "Dell",
        "im": ["dell-dell-inspiron-15-core-i5-8-512-1.jpg", "dell-dell-inspiron-15-core-i5-8-512-2.jpg", "dell-dell-inspiron-15-core-i5-8-512-3.jpg"],
        "q": "Dell Inspiron 15"
    },
    {
        "n": "Dell Inspiron 14 Core i5 16/512", "c": "Laptop", "pr": 10499000, "o": 11499000, "t": "laptop",
        "col": ["#363c45", "#8c98a8"], "b": "Dell",
        "im": ["dell-inspiron-14-1.jpg"],
        "q": "Dell Inspiron 14 platinum silver"
    },
    {
        "n": "Dell Inspiron 15 Core i3 8/256", "c": "Laptop", "pr": 6799000, "o": 7299000, "t": "laptop",
        "col": ["#29313d", "#71859e"], "b": "Dell",
        "im": ["dell-inspiron-15-i3-1.jpg"],
        "q": "Dell Inspiron 15 3520 carbon black"
    },
    {
        "n": "Dell Vostro 3520 Core i5", "c": "Laptop", "pr": 8999000, "o": 9699000, "t": "laptop",
        "col": ["#202630", "#5c6d85"], "b": "Dell",
        "im": ["dell-vostro-3520-1.jpg"],
        "q": "Dell Vostro 3520 black"
    },
    {
        "n": "Dell Latitude 3440 Core i5", "c": "Laptop", "pr": 11999000, "o": 12999000, "t": "laptop",
        "col": ["#1f242c", "#53637a"], "b": "Dell",
        "im": ["dell-latitude-3440-1.jpg"],
        "q": "Dell Latitude 3440 titan gray"
    },

    # ---------------- MSI (10 items) ----------------
    {
        "n": "MSI Raider GE78 HX RTX 4080", "c": "Laptop", "pr": 42999000, "o": 46999000, "t": "laptop",
        "col": ["#141417", "#ff0055"], "b": "MSI",
        "im": ["msi-raider-ge78-hx-1.jpg"],
        "q": "MSI Raider GE78 HX"
    },
    {
        "n": "MSI Stealth 16 Studio RTX 4070", "c": "Laptop", "pr": 31999000, "o": 34999000, "t": "laptop",
        "col": ["#1f242b", "#3d82a6"], "b": "MSI",
        "im": ["msi-stealth-16-studio-1.jpg"],
        "q": "MSI Stealth 16 Studio star blue"
    },
    {
        "n": "MSI Katana 15 Core i7 RTX 4060", "c": "Laptop", "pr": 17499000, "o": 18999000, "t": "laptop",
        "col": ["#1a1a1c", "#ff2a2a"], "b": "MSI",
        "im": ["msi-katana-15-1.jpg"],
        "q": "MSI Katana 15 black"
    },
    {
        "n": "MSI Cyborg 15 Core i5 RTX 4050", "c": "Laptop", "pr": 13999000, "o": 14999000, "t": "laptop",
        "col": ["#202730", "#00c8ff"], "b": "MSI",
        "im": ["msi-cyborg-15-1.jpg"],
        "q": "MSI Cyborg 15 translucent black"
    },
    {
        "n": "MSI Thin 15 Core i5 RTX 2050", "c": "Laptop", "pr": 9999000, "o": 10999000, "t": "laptop",
        "col": ["#1f2226", "#e63946"], "b": "MSI",
        "im": ["msi-thin-15-1.jpg"],
        "q": "MSI Thin 15 cosmos gray"
    },
    {
        "n": "MSI Bravo 15 Ryzen 5 RTX 4050", "c": "Laptop", "pr": 12499000, "o": 13499000, "t": "laptop",
        "col": ["#1e2424", "#00cc88"], "b": "MSI",
        "im": ["msi-bravo-15-1.jpg"],
        "q": "MSI Bravo 15 black"
    },
    {
        "n": "MSI Prestige 14 AI Studio Ultra 7", "c": "Laptop", "pr": 21999000, "o": 23999000, "t": "laptop",
        "col": ["#28323d", "#7496bd"], "b": "MSI",
        "im": ["msi-prestige-14-ai-1.jpg"],
        "q": "MSI Prestige 14 AI Studio stellar gray"
    },
    {
        "n": "MSI Modern 15 Core i7", "c": "Laptop", "pr": 10999000, "o": 11999000, "t": "laptop",
        "col": ["#1c2936", "#5782ab"], "b": "MSI",
        "im": ["msi-modern-15-1.jpg"],
        "q": "MSI Modern 15 classic black"
    },
    {
        "n": "MSI Modern 14 Core i5", "c": "Laptop", "pr": 8799000, "o": 9499000, "t": "laptop",
        "col": ["#1d2e3d", "#5aa9d6"], "b": "MSI",
        "im": ["msi-msi-modern-14-core-i5-1.jpg", "msi-msi-modern-14-core-i5-2.jpg", "msi-msi-modern-14-core-i5-3.jpg"],
        "q": "MSI Modern 14"
    },
    {
        "n": "MSI Modern 14 Core i3", "c": "Laptop", "pr": 6499000, "o": 6999000, "t": "laptop",
        "col": ["#24303b", "#6a8ba8"], "b": "MSI",
        "im": ["msi-modern-14-i3-1.jpg"],
        "q": "MSI Modern 14 urban silver"
    },

    # ---------------- ANKER (10 items) ----------------
    {
        "n": "Anker Power Bank 20.000 mAh 65W", "c": "Aksesoris", "pr": 499000, "o": 599000, "t": "bank",
        "col": ["#222", "#ff6a1a"], "b": "Anker",
        "im": ["anker-power-bank-20-000-mah-65w-1.jpg", "anker-power-bank-20-000-mah-65w-2.jpg", "anker-power-bank-20-000-mah-65w-3.jpg"],
        "q": "Anker power bank 20000 65w"
    },
    {
        "n": "Anker Power Bank 10.000 mAh 30W", "c": "Aksesoris", "pr": 349000, "o": 429000, "t": "bank",
        "col": ["#263342", "#4fa8f5"], "b": "Anker",
        "im": ["anker-power-bank-10-000-30w-1.jpg"],
        "q": "Anker power bank 10000 30W"
    },
    {
        "n": "Anker MagGo Power Bank Qi2 10.000 mAh", "c": "Aksesoris", "pr": 799000, "o": 949000, "t": "bank",
        "col": ["#363c45", "#9eb4d1"], "b": "Anker",
        "im": ["anker-maggo-qi2-10000-1.jpg"],
        "q": "Anker MagGo power bank Qi2 10000"
    },
    {
        "n": "Anker Charger GaN 65W 3 Port", "c": "Aksesoris", "pr": 349000, "o": 429000, "t": "plug",
        "col": ["#1f2937", "#22d3ee"], "b": "Anker",
        "im": ["anker-charger-gan-65w-3-port-1.jpg", "anker-charger-gan-65w-3-port-2.jpg", "anker-charger-gan-65w-3-port-3.jpg"],
        "q": "Anker GaN charger 65W 3 port"
    },
    {
        "n": "Anker Prime 67W GaN Wall Charger", "c": "Aksesoris", "pr": 599000, "o": 729000, "t": "plug",
        "col": ["#1c1f24", "#307fe2"], "b": "Anker",
        "im": ["anker-prime-67w-gan-1.jpg"],
        "q": "Anker Prime 67W charger"
    },
    {
        "n": "Anker 511 Charger Nano 3 30W", "c": "Aksesoris", "pr": 199000, "o": 249000, "t": "plug",
        "col": ["#5a4773", "#b79de3"], "b": "Anker",
        "im": ["anker-nano-3-30w-1.jpg"],
        "q": "Anker Nano 3 30W charger"
    },
    {
        "n": "Anker Soundcore Life Q30 ANC", "c": "Aksesoris", "pr": 899000, "o": 1099000, "t": "buds",
        "col": ["#1a1c22", "#d4af37"], "b": "Anker",
        "im": ["anker-soundcore-life-q30-1.jpg"],
        "q": "Soundcore Life Q30 black headphones"
    },
    {
        "n": "Anker Soundcore Space One ANC", "c": "Aksesoris", "pr": 1299000, "o": 1499000, "t": "buds",
        "col": ["#25303d", "#7aaed9"], "b": "Anker",
        "im": ["anker-soundcore-space-one-1.jpg"],
        "q": "Soundcore Space One headphones"
    },
    {
        "n": "Anker Soundcore R50i TWS", "c": "Aksesoris", "pr": 199000, "o": 259000, "t": "buds",
        "col": ["#1b1d21", "#3b82f6"], "b": "Anker",
        "im": ["anker-soundcore-r50i-1.jpg"],
        "q": "Soundcore R50i earbuds black"
    },
    {
        "n": "Anker USB-C Hub 7-in-1", "c": "Aksesoris", "pr": 449000, "o": 549000, "t": "plug",
        "col": ["#424854", "#9da8ba"], "b": "Anker",
        "im": ["anker-usb-c-hub-7-in-1-1.jpg"],
        "q": "Anker 7 in 1 USB C hub"
    },

    # ---------------- LOGITECH (10 items) ----------------
    {
        "n": "Logitech MX Master 3S Wireless Mouse", "c": "Aksesoris", "pr": 1599000, "o": 1799000, "t": "mouse",
        "col": ["#26282b", "#70737a"], "b": "Logitech",
        "im": ["logitech-mx-master-3s-1.jpg"],
        "q": "Logitech MX Master 3S graphite"
    },
    {
        "n": "Logitech MX Anywhere 3S Mouse", "c": "Aksesoris", "pr": 1199000, "o": 1399000, "t": "mouse",
        "col": ["#614552", "#c49bb0"], "b": "Logitech",
        "im": ["logitech-mx-anywhere-3s-1.jpg"],
        "q": "Logitech MX Anywhere 3S rose"
    },
    {
        "n": "Logitech M331 Silent Plus Mouse", "c": "Aksesoris", "pr": 249000, "o": 299000, "t": "mouse",
        "col": ["#2a2a2a", "#4b78ff"], "b": "Logitech",
        "im": ["logitech-m331-silent-mouse-1.jpg", "logitech-m331-silent-mouse-2.jpg", "logitech-m331-silent-mouse-3.jpg"],
        "q": "Logitech M331 Silent Mouse"
    },
    {
        "n": "Logitech Pebble Mouse 2 M350s", "c": "Aksesoris", "pr": 329000, "o": 399000, "t": "mouse",
        "col": ["#695444", "#d9bda9"], "b": "Logitech",
        "im": ["logitech-pebble-mouse-2-m350s-1.jpg"],
        "q": "Logitech Pebble Mouse 2 M350s"
    },
    {
        "n": "Logitech G502 HERO Gaming Mouse", "c": "Aksesoris", "pr": 699000, "o": 849000, "t": "mouse",
        "col": ["#111317", "#00c3ff"], "b": "Logitech",
        "im": ["logitech-g502-hero-1.jpg"],
        "q": "Logitech G502 HERO gaming mouse"
    },
    {
        "n": "Logitech G304 Lightspeed Wireless Mouse", "c": "Aksesoris", "pr": 499000, "o": 599000, "t": "mouse",
        "col": ["#1c1f26", "#00b4d8"], "b": "Logitech",
        "im": ["logitech-g304-lightspeed-1.jpg"],
        "q": "Logitech G304 Lightspeed black"
    },
    {
        "n": "Logitech K380 Multi-Device Keyboard", "c": "Aksesoris", "pr": 479000, "o": 549000, "t": "mouse",
        "col": ["#2e3d34", "#75a687"], "b": "Logitech",
        "im": ["logitech-k380-keyboard-1.jpg"],
        "q": "Logitech K380 keyboard graphite"
    },
    {
        "n": "Logitech MX Keys Mini Keyboard", "c": "Aksesoris", "pr": 1499000, "o": 1699000, "t": "mouse",
        "col": ["#363b45", "#9ca8ba"], "b": "Logitech",
        "im": ["logitech-mx-keys-mini-1.jpg"],
        "q": "Logitech MX Keys Mini grey"
    },
    {
        "n": "Logitech C922 Pro HD Webcam", "c": "Aksesoris", "pr": 1299000, "o": 1499000, "t": "mouse",
        "col": ["#181a1f", "#4b82d4"], "b": "Logitech",
        "im": ["logitech-c922-pro-1.jpg"],
        "q": "Logitech C922 Pro stream webcam"
    },
    {
        "n": "Logitech Zone Vibe 100 Headset", "c": "Aksesoris", "pr": 1399000, "o": 1599000, "t": "buds",
        "col": ["#3a3847", "#8c86ad"], "b": "Logitech",
        "im": ["logitech-zone-vibe-100-1.jpg"],
        "q": "Logitech Zone Vibe 100 graphite"
    },

    # ---------------- PRESERVED EXISTING SPECIAL ITEMS ----------------
    {
        "n": "Infinix Hot 50 8/128", "c": "HP", "pr": 1999000, "o": 2299000, "t": "phone",
        "col": ["#0b6b6b", "#68e6d9"], "b": "Infinix",
        "im": ["infinix-infinix-hot-50-8-128-1.jpg", "infinix-infinix-hot-50-8-128-2.jpg", "infinix-infinix-hot-50-8-128-3.jpg"],
        "q": "Infinix Hot 50"
    },
    {
        "n": "Tecno Spark 30 8/256", "c": "HP", "pr": 2099000, "o": 2399000, "t": "phone",
        "col": ["#1f4fd1", "#a7c0ff"], "b": "Tecno",
        "im": ["tecno-tecno-spark-30-8-256-1.jpg", "tecno-tecno-spark-30-8-256-2.jpg", "tecno-tecno-spark-30-8-256-3.jpg"],
        "q": "Tecno Spark 30"
    },
    {
        "n": "Axioo Hype 5 Ryzen 5", "c": "Laptop", "pr": 6499000, "o": 6999000, "t": "laptop",
        "col": ["#2a2a2a", "#9a9a9a"], "b": "Axioo",
        "im": ["axioo-axioo-hype-5-ryzen-5-1.jpg", "axioo-axioo-hype-5-ryzen-5-2.jpg", "axioo-axioo-hype-5-ryzen-5-3.jpg"],
        "q": "Axioo Hype 5"
    },
    {
        "n": "Baseus Kabel Data USB-C 100W 2m", "c": "Aksesoris", "pr": 129000, "o": 169000, "t": "plug",
        "col": ["#e5e7eb", "#9ca3af"], "b": "Baseus",
        "im": ["baseus-kabel-data-usb-c-100w-2m-1.jpg", "baseus-kabel-data-usb-c-100w-2m-2.jpg", "baseus-kabel-data-usb-c-100w-2m-3.jpg"],
        "q": "Baseus USB-C cable 100W"
    }
]

BLOCKED = ["shutterstock", "alamy", "istockphoto", "gettyimages", "dreamstime", "depositphotos",
           "vecteezy", "freepik", "vector", "drawing", "illustration", "wallpaper", "avatar", "icon"]

def download_and_save(url, out_path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            if img.width < 250 or img.height < 250:
                return False
            # Check aspect ratio
            ratio = img.width / img.height
            if ratio < 0.45 or ratio > 2.2:
                return False
            img = img.convert("RGB")
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
            img.save(out_path, "JPEG", quality=85)
            return True
    except Exception as e:
        pass
    return False

def find_image_for_product(prod):
    target_file = prod["im"][0]
    if os.path.exists(target_file) and os.path.getsize(target_file) > 10000:
        return True

    query = prod.get("q", prod["n"])
    tokens = [t.lower() for t in re.findall(r"[A-Za-z0-9]+", query) if t.lower() not in ["official", "product", "5g", "4g", "8", "16", "256", "512", "128", "gb", "inch"]]

    # 1. Search DDG
    try:
        ddg_results = list(DDGS().images(f"{query} white background", max_results=15))
        for res in ddg_results:
            img_url = res.get("image", "")
            title = (res.get("title", "") + " " + img_url).lower()
            if any(b in title for b in BLOCKED):
                continue
            # At least 2 tokens must match
            matches = sum(1 for t in tokens if t in title)
            if matches >= min(2, len(tokens)):
                if download_and_save(img_url, target_file):
                    print(f"  [DDG OK] {prod['n']} -> {target_file}")
                    return True
    except Exception as e:
        print(f"  [DDG Err] {e}")

    # 2. Bing Image fallback
    try:
        u = f"https://www.bing.com/images/async?q={requests.utils.quote(query + ' product photo')}&first=0&count=15&adlt=off"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(u, headers=headers, timeout=10).text
        matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', res)
        for m in matches:
            img_url = requests.utils.unquote(m)
            if any(b in img_url.lower() for b in BLOCKED):
                continue
            if download_and_save(img_url, target_file):
                print(f"  [Bing OK] {prod['n']} -> {target_file}")
                return True
    except Exception as e:
        print(f"  [Bing Err] {e}")

    return False

def main():
    print(f"Starting catalog update for {len(PRODUCTS)} products across 16 brands...")
    success = 0
    for idx, p in enumerate(PRODUCTS, 1):
        target_file = p["im"][0]
        if os.path.exists(target_file) and os.path.getsize(target_file) > 10000:
            success += 1
            continue
        print(f"[{idx}/{len(PRODUCTS)}] Fetching photo for: {p['b']} - {p['n']}...")
        ok = find_image_for_product(p)
        if ok:
            success += 1
        else:
            print(f"  [Warning] Could not fetch photo for {p['n']}, will use vector art fallback.")
        time.sleep(0.5)

    print(f"\nPhoto fetch completed: {success}/{len(PRODUCTS)} products have photos.")

    # Now update index.html
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Build JS string for P
    lines = ["var P=["]
    for p in PRODUCTS:
        # Replicate im to 3 items if only 1 image exists so gallery modal works seamlessly
        im_list = p["im"]
        if len(im_list) == 1:
            im_list = [im_list[0], im_list[0], im_list[0]]
        im_json = json.dumps(im_list)
        col_json = json.dumps(p["col"])
        name_esc = p["n"].replace('"', '\\"')
        lines.append(f'{{n:"{name_esc}",c:"{p["c"]}",pr:{p["pr"]},o:{p["o"]},t:"{p["t"]}",col:{col_json},b:"{p["b"]}",im:{im_json}}},')
    lines[-1] = lines[-1].rstrip(',') # remove trailing comma
    lines.append("];")
    new_p_js = "\n".join(lines)

    # Replace var P=[...]; in index.html
    p_pattern = re.compile(r'var P=\[.*?\];', re.DOTALL)
    if p_pattern.search(html):
        html = p_pattern.sub(new_p_js, html)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Successfully updated index.html with 160+ products!")
    else:
        print("ERROR: Could not locate var P=[...]; in index.html")

if __name__ == "__main__":
    main()
