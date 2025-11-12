import os
from pymongo import MongoClient
from supermemory import Supermemory
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# Initialize clients
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["BackendSymtheticData"]

supermemory_client = Supermemory(
    api_key=os.getenv("SUPERMEMORY_API_KEY"),
)

# Rate limiting helper
def rate_limit_sleep(delay=0.5):
    """Add delay between API calls to avoid rate limiting"""
    time.sleep(delay)


def format_blocker(doc):
    """Convert blocker document to readable memory content"""
    content = f"""BLOCKER REPORT [{doc['id']}]
Title: {doc['title']}

Core Issue: {doc['core_issue']}

Root Cause: {doc['root_cause']}

Solution: {doc['solution']}

Resolved By: {doc['resolved_by']}

Tags: {', '.join(doc['tags'])}

[Document Type: Blocker | ID: {doc['id']}]"""
    return content


def format_keywords(doc):
    """Convert keywords document to readable memory content"""
    # Remove MongoDB _id field
    keywords = {k: v for k, v in doc.items() if k != '_id'}
    
    content = "COMPANY KEYWORDS & DEFINITIONS\n\n"
    for term, definition in keywords.items():
        content += f"• {term}: {definition}\n"
    
    content += "\n[Document Type: Keywords Dictionary]"
    return content


def format_project(doc):
    """Convert project document to readable memory content"""
    milestones_text = ""
    if 'milestones' in doc and doc['milestones']:
        milestones_text = "\n\nMilestones:\n"
        for ms in doc['milestones']:
            milestones_text += f"  • {ms['name']} (Due: {ms.get('due_data', 'N/A')}) - Status: {ms['status']}\n"
    
    content = f"""PROJECT [{doc['id']}]
Name: {doc['name']}

Description: {doc['description']}

Status: {doc['status']}{milestones_text}

[Document Type: Project | ID: {doc['id']}]"""
    return content


def format_team_member(doc):
    """Convert team member document to readable memory content"""
    skills_text = ', '.join(doc['skills'])
    
    content = f"""TEAM MEMBER [{doc['id']}]
Name: {doc['name']}
Role: {doc['role']}

Current Task: {doc['current_task']}

Skills: {skills_text}

Project Responsibilities: {doc['project_responsibilities']}

Contact:
  • Slack: {doc['contact']['slack']}
  • Email: {doc['contact']['email']}

Timezone: {doc['timezone']}

[Document Type: Team Member | ID: {doc['id']}]"""
    return content


def format_ticket(doc):
    """Convert ticket document to readable memory content"""
    tags_text = ', '.join(doc['tags'])
    dependencies_text = ', '.join(doc.get('dependencies', [])) if doc.get('dependencies') else 'None'
    
    content = f"""TICKET [{doc['id']}]
Title: {doc['title']}

Project: {doc['project_id']}

Description: {doc['description']}

Assignee: {doc['assignee']} ({doc['assignee_email']})

Status: {doc['status']}
Priority: {doc['priority']}
Milestone: {doc.get('milestone', 'N/A')}

Created: {doc['created_at']}
Updated: {doc['updated_at']}

Root Cause: {doc.get('root_cause', 'Not yet determined')}
Solution: {doc.get('solution', 'In progress')}

Tags: {tags_text}
Dependencies: {dependencies_text}
Comments: {doc.get('comments_count', 0)}

[Document Type: Ticket | ID: {doc['id']} | Project: {doc['project_id']}]"""
    return content


def push_collection(collection_name, formatter_func):
    """Push all documents from a collection to Supermemory"""
    print(f"\n{'='*60}")
    print(f"Processing collection: {collection_name}")
    print(f"{'='*60}")
    
    collection = db[collection_name]
    total_docs = collection.count_documents({})
    print(f"Total documents: {total_docs}")
    
    success_count = 0
    error_count = 0
    
    for idx, doc in enumerate(collection.find(), 1):
        try:
            content = formatter_func(doc)
            
            # Push to Supermemory
            supermemory_client.memories.add(content=content)
            
            success_count += 1
            print(f"✓ [{idx}/{total_docs}] Pushed: {doc.get('id', doc.get('_id'))}")
            
            # Rate limiting
            rate_limit_sleep()
            
        except Exception as e:
            error_count += 1
            print(f"✗ [{idx}/{total_docs}] Error pushing {doc.get('id', doc.get('_id'))}: {str(e)}")
            # Continue with next document even if one fails
            continue
    
    print(f"\n{collection_name} Summary:")
    print(f"  ✓ Success: {success_count}")
    print(f"  ✗ Errors: {error_count}")
    return success_count, error_count


def main():
    """Main execution function"""
    print("="*60)
    print("MongoDB to Supermemory Migration")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_success = 0
    total_errors = 0
    
    # Process each collection
    collections = [
        ('blockers', format_blocker),
        ('keywords', format_keywords),
        ('projects', format_project),
        ('teamMembers', format_team_member),
        ('tickets', format_ticket),
    ]
    
    for collection_name, formatter in collections:
        success, errors = push_collection(collection_name, formatter)
        total_success += success
        total_errors += errors
    
    # Final summary
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print(f"Total documents pushed: {total_success}")
    print(f"Total errors: {total_errors}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()