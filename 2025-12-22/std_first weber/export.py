from mongoengine import connect
import json
import logging

from settings import MONGO_DB, MONGO_HOST, MONGO_PORT
from items import AgentDataItem



class JsonExporter:
    """Export agent data from MongoDB to JSON"""

    def __init__(self):
        connect(db=MONGO_DB,host=MONGO_HOST,port=MONGO_PORT,alias="default")
        self.collection = AgentDataItem.objects

    def export_to_json(self, output_file="firstweber_agents.json"):
        """Export all agent data to a JSON file"""
        count = self.collection.count()
        if count == 0:
            logging.warning("No data to export.")
            return

        logging.info(f"Exporting {count} records to {output_file}")

        data_list = []
        for agent in self.collection:
            item = {
                "profile_url": getattr(agent, "profile_url", "") or "",
                "first_name": getattr(agent, "first_name", "") or "",
                "middle_name": getattr(agent, "middle_name", "") or "",
                "last_name": getattr(agent, "last_name", "") or "",
                "title": getattr(agent, "title", "") or "",
                "description": getattr(agent, "description", "") or "",
                "address": getattr(agent, "address", "") or "",
                "street_address": getattr(agent, "street_address", "") or "",
                "city": getattr(agent, "city", "") or "",
                "state": getattr(agent, "state", "") or "",
                "zip_code": getattr(agent, "zip_code", "") or "",
                "country": getattr(agent, "country", "") or "",
                "languages": getattr(agent, "languages", "") or "",
                "website": getattr(agent, "website", "") or "",
                "social_links": getattr(agent, "social_links", []) or [],
                "image_url": getattr(agent, "image_url", "") or "",
                "agent_phone_numbers": getattr(agent, "agent_phone_numbers", "") or ""
            }
            data_list.append(item)

        # Write JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)

        logging.info(f"Export complete: {output_file}")


if __name__ == "__main__":
    exporter = JsonExporter()
    exporter.export_to_json()
