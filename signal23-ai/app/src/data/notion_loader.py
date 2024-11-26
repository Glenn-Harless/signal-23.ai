from typing import List, Dict, Optional
from notion_client import Client
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class NotionPage(BaseModel):
    """Represents a page from Notion"""
    id: str
    title: str
    content: str
    url: str
    last_edited: str
    metadata: Dict[str, any]

class NotionLoader:
    """Loads and processes content from Notion"""
    def __init__(self, token: str):
        self.client = Client(auth=token)
    
    async def load_database(self, database_id: str) -> List[NotionPage]:
        """Load all pages from a Notion database"""
        try:
            pages = []
            query = self.client.databases.query(database_id=database_id)
            
            for page in query['results']:
                # Extract page content
                blocks = self.client.blocks.children.list(block_id=page['id'])
                content = self._extract_content(blocks['results'])
                
                # Create NotionPage object
                page_data = NotionPage(
                    id=page['id'],
                    title=self._extract_title(page),
                    content=content,
                    url=page['url'],
                    last_edited=page['last_edited_time'],
                    metadata={
                        'created_time': page['created_time'],
                        'properties': self._extract_properties(page)
                    }
                )
                pages.append(page_data)
            
            logger.info(f"Loaded {len(pages)} pages from Notion database")
            return pages
            
        except Exception as e:
            logger.error(f"Error loading Notion database: {str(e)}")
            raise

    def _extract_content(self, blocks: List[Dict]) -> str:
        """Extract text content from Notion blocks"""
        content = []
        for block in blocks:
            if block['type'] == 'paragraph':
                text = block['paragraph']['rich_text']
                content.append(self._get_text_from_rich_text(text))
            elif block['type'] == 'heading_1':
                text = block['heading_1']['rich_text']
                content.append(f"# {self._get_text_from_rich_text(text)}")
            elif block['type'] == 'heading_2':
                text = block['heading_2']['rich_text']
                content.append(f"## {self._get_text_from_rich_text(text)}")
            elif block['type'] == 'bulleted_list_item':
                text = block['bulleted_list_item']['rich_text']
                content.append(f"- {self._get_text_from_rich_text(text)}")
        
        return "\n\n".join(content)

    def _get_text_from_rich_text(self, rich_text: List[Dict]) -> str:
        """Extract plain text from Notion's rich text format"""
        return " ".join([text['plain_text'] for text in rich_text])

    def _extract_title(self, page: Dict) -> str:
        """Extract page title from Notion page object"""
        title_prop = next((prop for prop in page['properties'].values() 
                          if prop['type'] == 'title'), None)
        if title_prop and title_prop['title']:
            return self._get_text_from_rich_text(title_prop['title'])
        return "Untitled"

    def _extract_properties(self, page: Dict) -> Dict:
        """Extract page properties from Notion page object"""
        properties = {}
        for name, prop in page['properties'].items():
            if prop['type'] == 'rich_text':
                properties[name] = self._get_text_from_rich_text(prop['rich_text'])
            elif prop['type'] == 'select':
                properties[name] = prop['select']['name'] if prop['select'] else None
            elif prop['type'] == 'multi_select':
                properties[name] = [option['name'] for option in prop['multi_select']]
            elif prop['type'] == 'date':
                properties[name] = prop['date']['start'] if prop['date'] else None
        return properties