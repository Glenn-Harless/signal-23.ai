from typing import List, Dict, Optional, Any
from notion_client import Client
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class NotionProperties(BaseModel):
    Notes: Optional[str] = ''
    category: Optional[str] = ''
    Tags: Optional[List[str]] = []
    Description: Optional[str] = ''

class NotionMetadata(BaseModel):
    created_time: str
    properties: Dict[str, Any]

class NotionPage(BaseModel):
    id: str
    title: str
    content: str
    url: str
    last_edited: str
    metadata: NotionMetadata

from typing import List, Dict, Optional, Any
from notion_client import Client
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class NotionProperties(BaseModel):
    Notes: Optional[str] = ''
    category: Optional[str] = ''
    Tags: Optional[List[str]] = []
    Description: Optional[str] = ''

class NotionMetadata(BaseModel):
    created_time: str
    properties: Dict[str, Any]

class NotionPage(BaseModel):
    id: str
    title: str
    content: str
    url: str
    last_edited: str
    metadata: NotionMetadata


logger = logging.getLogger(__name__)

class NotionLoader:
    def __init__(self, token: str):
        self.client = Client(auth=token)
    
    def load_database(self, database_id: str) -> List[NotionPage]:
        """Load all pages from a Notion database"""
        try:
            # First, try to get the database itself to verify access
            print(f"Attempting to access database with ID: {database_id}")
            database = self.client.databases.retrieve(database_id=database_id)
            print(f"Successfully accessed database: {database.get('title', [{}])[0].get('text', {}).get('content', 'Untitled')}")
            
            pages = []
            print("Querying database for pages...")
            
            # Query with filter to get all pages
            query = self.client.databases.query(
                database_id=database_id,
                page_size=100  # Adjust if you have more pages
            )
            
            print(f"Found {len(query['results'])} pages in database")
            
            for page in query['results']:
                try:
                    print(f"Processing page: {page['id']}")
                    
                    # Get page content
                    blocks = self.client.blocks.children.list(block_id=page['id'])
                    content = self._extract_content(blocks['results'])
                    
                    title = self._extract_title(page)
                    print(f"Extracted title: {title}")
                    
                    # Create NotionPage object
                    page_data = NotionPage(
                        id=page['id'],
                        title=title,
                        content=content,
                        url=page['url'],
                        last_edited=page['last_edited_time'],
                        metadata=NotionMetadata(
                            created_time=page['created_time'],
                            properties=self._extract_properties(page)
                        )
                    )
                    pages.append(page_data)
                    print(f"Successfully processed page: {title}")
                    
                except Exception as e:
                    print(f"Error processing page {page['id']}: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
            
            print(f"Successfully processed {len(pages)} pages")
            return pages
            
        except Exception as e:
            print(f"Error accessing Notion database: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise
            
    def _extract_title(self, page: Dict) -> str:
        """Extract page title from Notion page object"""
        # Get the title property
        title_prop = None
        for prop_id, prop in page['properties'].items():
            if prop['type'] == 'title':
                title_prop = prop
                break
        
        if title_prop and title_prop['title']:
            # Extract text from the title
            return self._get_text_from_rich_text(title_prop['title'])
        return "Untitled"

    def _get_text_from_rich_text(self, rich_text: List[Dict]) -> str:
        """Extract plain text from Notion's rich text format"""
        return " ".join([text['plain_text'] for text in rich_text])

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