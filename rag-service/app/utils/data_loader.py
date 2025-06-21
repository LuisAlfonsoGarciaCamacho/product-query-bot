from typing import List
import json
from pathlib import Path


class DataLoader:
    """Utility class for loading sample data"""
    
    @staticmethod
    def load_sample_products() -> list[str]:
        """Load sample product data"""
        return [
            "iPhone 15 Pro: Premium smartphone with A17 Pro chip, 48MP camera system, titanium design, and USB-C. Available in 128GB, 256GB, 512GB, 1TB storage options.",
            "MacBook Air M3: Ultra-thin laptop with M3 chip, 13.6-inch Liquid Retina display, up to 18 hours battery life, and 8GB unified memory.",
            "AirPods Pro (3rd gen): Wireless earbuds with adaptive transparency, personalized spatial audio, and up to 6 hours listening time with ANC.",
            "Apple Watch Series 9: Advanced smartwatch with S9 chip, always-on Retina display, health monitoring, and up to 18 hours battery life.",
            "iPad Air (5th gen): Versatile tablet with M1 chip, 10.9-inch Liquid Retina display, Touch ID, and compatibility with Apple Pencil (2nd gen).",
            "Samsung Galaxy S24 Ultra: Flagship Android phone with 200MP camera, S Pen, 6.8-inch Dynamic AMOLED display, and AI-powered features.",
            "Dell XPS 13: Premium ultrabook with Intel Core i7, 13.4-inch InfinityEdge display, 16GB RAM, and 512GB SSD storage.",
            "Sony WH-1000XM5: Premium wireless headphones with industry-leading noise cancellation, 30-hour battery life, and multipoint connection.",
            "Google Pixel 8 Pro: AI-powered smartphone with advanced computational photography, 6.7-inch LTPO OLED display, and 7 years of updates.",
            "Microsoft Surface Pro 9: 2-in-1 laptop tablet with Intel Core i7, 13-inch PixelSense touchscreen, and up to 15.5 hours battery life."
        ]
    
    @staticmethod
    def save_products_to_file(products: List[str], filepath: str = "data/products.json"):
        """Save products to JSON file"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(products, f, indent=2)
    
    @staticmethod
    def load_products_from_file(filepath: str = "data/products.json") -> List[str]:
        """Load products from JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return DataLoader.load_sample_products()