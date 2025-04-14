# recipes/management/commands/import_recipes.py
import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Recipe  # Đảm bảo đường dẫn import đúng
import os


class Command(BaseCommand):
    help = "Imports recipes from the specified CSV file into the database"

    def add_arguments(self, parser):
        parser.add_argument("csv_file_path", type=str, help="The path to the CSV file")

    def handle(self, *args, **options):
        csv_file_path = options["csv_file_path"]

        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f"CSV file not found at {csv_file_path}")
            )
            return

        try:
            df = pd.read_csv(csv_file_path)
            self.stdout.write(f"Reading CSV file: {csv_file_path}...")

            # Đảm bảo các cột cần thiết tồn tại
            required_cols = [
                "Title",
                "Cleaned_Ingredients",
                "Instructions",
                "Image_Name",
            ]
            if not all(col in df.columns for col in required_cols):
                self.stdout.write(
                    self.style.ERROR(
                        f"CSV must contain columns: {', '.join(required_cols)}"
                    )
                )
                return

            recipes_to_create = []
            count = 0
            skipped = 0
            for index, row in df.iterrows():
                # Kiểm tra xem original_index đã tồn tại chưa để tránh lỗi unique
                if not Recipe.objects.filter(original_index=index).exists():
                    recipes_to_create.append(
                        Recipe(
                            title=row["Title"],
                            cleaned_ingredients=row["Cleaned_Ingredients"],
                            instructions=row["Instructions"],
                            image_name=row["Image_Name"],
                            original_index=index,  # Lưu index gốc
                        )
                    )
                    count += 1
                else:
                    skipped += 1

            if recipes_to_create:
                Recipe.objects.bulk_create(recipes_to_create)
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully imported {count} new recipes.")
                )
            else:
                self.stdout.write(self.style.WARNING("No new recipes to import."))

            if skipped > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped {skipped} recipes (original_index already exists)."
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
