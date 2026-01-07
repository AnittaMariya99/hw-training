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

    def export_to_json(self, output_file="alliebeth agents/alliebeth_agents.json"):
        """Export all agent data to a JSON file"""
        count = self.collection.count()
        if count == 0:
            logging.warning("No data to export.")
            return

        logging.info(f"Exporting {count} records to {output_file}")

        # Write JSON Lines
        with open(output_file, "w", encoding="utf-8") as f:
            for agent in self.collection:
                item = {}
                item["profile_url"] = getattr(agent, "profile_url", "") or ""
                item["first_name"] = getattr(agent, "first_name", "") or ""
                item["middle_name"] = getattr(agent, "middle_name", "") or ""
                item["last_name"] = getattr(agent, "last_name", "") or ""
                item["title"] = getattr(agent, "title", "") or ""
                item["description"] = getattr(agent, "description", "") or ""
                item["address"] = getattr(agent, "address", "") or ""
                item["street_address"] = getattr(agent, "street_address", "") or ""
                item["city"] = getattr(agent, "city", "") or ""
                item["state"] = getattr(agent, "state", "") or ""
                item["zip_code"] = getattr(agent, "zip_code", "") or ""
                item["country"] = getattr(agent, "country", "") or ""
                item["languages"] = getattr(agent, "languages", "") or ""
                item["website"] = getattr(agent, "website", "") or ""
                item["social_links"] = getattr(agent, "social_links", []) or []
                item["image_url"] = getattr(agent, "image_url", "") or ""
                item["agent_phone_numbers"] = getattr(agent, "agent_phone_numbers", "") or ""
                
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        logging.info(f"Export complete: {output_file}")


if __name__ == "__main__":
    exporter = JsonExporter()
    exporter.export_to_json()
