"""
Vendor Categorization Module for Finance App

This module handles categorizing transactions based on vendor names.
"""

import pandas as pd
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VendorCategorizer:
    """Categorize transactions based on vendor names."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the vendor categorizer.

        Args:
            config_path: Path to the vendor categories JSON config file
        """
        self.config_path = config_path or Path(__file__).parent / "config" / "vendor_categories.json"
        self.categories = self._load_categories()

    def _load_categories(self) -> Dict[str, List[str]]:
        """
        Load vendor categories from config file.

        Returns:
            Dictionary mapping category names to lists of vendor patterns
        """
        try:
            with open(self.config_path, 'r') as f:
                categories = json.load(f)
            logger.info(f"Loaded {len(categories)} categories from {self.config_path}")
            return categories
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}, using default categories")
            return self._get_default_categories()
        except Exception as e:
            logger.error(f"Error loading categories: {str(e)}")
            return self._get_default_categories()

    def _get_default_categories(self) -> Dict[str, List[str]]:
        """
        Get default vendor categories.

        Returns:
            Dictionary of default categories and patterns
        """
        return {
            "Groceries": ["walmart", "target", "kroger", "safeway", "whole foods", "trader joe", "costco"],
            "Restaurants": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "burger", "pizza", "chipotle"],
            "Transportation": ["uber", "lyft", "gas", "fuel", "shell", "chevron", "exxon", "transit", "parking"],
            "Utilities": ["electric", "power", "water", "gas", "internet", "phone", "verizon", "at&t", "comcast"],
            "Entertainment": ["netflix", "spotify", "hulu", "amazon prime", "disney", "movie", "theater", "concert"],
            "Shopping": ["amazon", "ebay", "etsy", "best buy", "home depot", "lowe's", "macy", "nordstrom"],
            "Healthcare": ["pharmacy", "cvs", "walgreens", "hospital", "clinic", "doctor", "medical", "dental"],
            "Insurance": ["insurance", "geico", "state farm", "allstate", "progressive"],
            "Subscription": ["subscription", "membership", "monthly fee", "annual fee"],
            "Other": []
        }

    def categorize_vendor(self, vendor_name: str) -> str:
        """
        Categorize a single vendor based on its name.

        Args:
            vendor_name: Name of the vendor

        Returns:
            Category name
        """
        if pd.isna(vendor_name):
            return "Unknown"

        vendor_lower = str(vendor_name).lower()

        # Check each category's patterns
        for category, patterns in self.categories.items():
            if category == "Other":
                continue

            for pattern in patterns:
                # Use word boundaries for better matching
                if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', vendor_lower) or \
                   pattern.lower() in vendor_lower:
                    return category

        return "Other"

    def categorize_transactions(self, df: pd.DataFrame, vendor_column: str = 'vendor') -> pd.DataFrame:
        """
        Categorize all transactions in a DataFrame.

        Args:
            df: DataFrame with transaction data
            vendor_column: Name of the column containing vendor names

        Returns:
            DataFrame with added 'category' column
        """
        df = df.copy()

        if vendor_column not in df.columns:
            logger.error(f"Column '{vendor_column}' not found in DataFrame")
            df['category'] = "Unknown"
            return df

        # Apply categorization
        df['category'] = df[vendor_column].apply(self.categorize_vendor)

        logger.info(f"Categorized {len(df)} transactions into {df['category'].nunique()} categories")
        return df

    def get_category_summary(self, df: pd.DataFrame, amount_column: str = 'amount') -> pd.DataFrame:
        """
        Get a summary of spending by category.

        Args:
            df: DataFrame with categorized transactions
            amount_column: Name of the column containing transaction amounts

        Returns:
            DataFrame with category summaries
        """
        if 'category' not in df.columns:
            logger.error("DataFrame does not have 'category' column. Run categorize_transactions first.")
            return pd.DataFrame()

        # Calculate summary statistics by category
        summary = df.groupby('category').agg({
            amount_column: ['sum', 'mean', 'count']
        }).round(2)

        summary.columns = ['total', 'average', 'count']
        summary = summary.sort_values('total', ascending=False)
        summary['percentage'] = (summary['total'] / summary['total'].sum() * 100).round(2)

        return summary.reset_index()

    def add_custom_rule(self, category: str, patterns: List[str]):
        """
        Add custom categorization rules.

        Args:
            category: Category name
            patterns: List of patterns to match for this category
        """
        if category in self.categories:
            self.categories[category].extend(patterns)
        else:
            self.categories[category] = patterns

        logger.info(f"Added {len(patterns)} patterns to category '{category}'")

    def save_categories(self, output_path: Optional[str] = None):
        """
        Save current categories to a JSON file.

        Args:
            output_path: Path to save the categories (default: original config path)
        """
        save_path = output_path or self.config_path

        # Create directory if it doesn't exist
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(save_path, 'w') as f:
                json.dump(self.categories, f, indent=2)
            logger.info(f"Saved categories to {save_path}")
        except Exception as e:
            logger.error(f"Error saving categories: {str(e)}")
