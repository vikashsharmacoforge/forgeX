import os
import sys
import asyncio
import json
clients_path = os.path.abspath("./src/mcp-clients")
# rag_path = os.path.abspath("/src/memory/lightrag")
sys.path.append(clients_path)
from stmhttp_client import MCPClient
# sys.append(rag_path)



async def call_tool_():
    try:
        client = MCPClient()
        await client.connect_to_streamable_http_server("http://localhost:6001/mcp/")
        # print( await client.session.list_tools())
        response = await client.session.call_tool(
            name="lightrag_new_tool", 
            arguments={
                        "domain": "User Stories",
                        "question": "what are best practices for creating user stories?",
                        "history": []
                    }
        )
        
        print("response:" , json.loads(response.content[0].text).get('LightRAG',str))
    finally:
        if client:
            await client.cleanup()
    

asyncio.run(call_tool_())

response = """
Based on your request to create a rate management system and the provided context about the Rates Hub project, I'll compile a comprehensive set of requirements. Let me present the current project requirements that combine both the initial understanding and what we've discussed:

## **Current Project Requirements for Rate Management System**

### **1. Project Overview**
- **System Name**: Rates Hub - A centralized rate management platform
- **Purpose**: Transform rate management processes by replacing manual, Excel-based methods with an automated, web-based solution
- **Scope**: Manage deposit rates, index rates, and various financial product rates across the organization

### **2. Key Stakeholders and Users**
- **Rates Committee Members**: Set, approve, and publish rates
- **Branch Bankers**: Access daily rate cards specific to their branch/region
- **System Administrators**: Manage users, permissions, and system configuration
- **External Applications**: Consume rates via API endpoints
- **Compliance/Audit Teams**: Review rate change history and audit trails

### **3. Functional Requirements**

#### **3.1 Rate Management**
- Automated daily rate fetching and display via scheduled tasks
- Support for multiple rate types (deposit rates, loan rates, index rates)
- Rate adjustment capabilities with proper authorization
- Version control for all rate changes
- Bulk rate import/export functionality

#### **3.2 Workflow & Approvals**
- Multi-level approval workflow for rate changes
- Role-based permissions (viewer, editor, approver, admin)
- Email notifications for pending approvals
- Audit trail for all rate modifications

#### **3.3 Data Management**
- Historical rate storage with timestamps
- Advanced search and filtering capabilities
- Data retention policies
- Automated archival of old rates

#### **3.4 Integration Capabilities**
- Real-time API endpoints for rate distribution
- Integration with FIS Core Banking Platform
- MuleSoft integration for third-party rate providers
- Export functionality to FIS rates plans
- Support for multiple data formats (JSON, XML, CSV)

#### **3.5 User Interface**
- Web-based dashboard for rate management
- Customizable rate cards by branch/region
- Real-time rate display updates
- Mobile-responsive design
- Intuitive search and filter interface

### **4. Non-Functional Requirements**

#### **4.1 Performance**
- Support for concurrent users (specify number needed)
- Rate updates processed within specified time windows
- API response time under 2 seconds
- System availability of 99.9%

#### **4.2 Security**
- OAuth 2.0 or JWT authentication
- Role-based access control (RBAC)
- Data encryption at rest and in transit
- Secure API endpoints
- Session management and timeout controls

#### **4.3 Scalability**
- Containerized deployment using Docker
- Cloud-ready architecture (Azure)
- Horizontal scaling capabilities
- Load balancing support

### **5. Technical Requirements**
- **Backend**: .NET 8 framework
- **Database**: PostgreSQL for time-series data
- **Frontend**: React (with Angular as alternative)
- **Integration**: MuleSoft for API management
- **Deployment**: Docker containers on Azure
- **Monitoring**: Application performance monitoring tools

### **6. Business Benefits**
- Eliminate manual rate distribution processes
- Reduce operational errors and risks
- Improve rate accuracy and timeliness
- Enable real-time rate access across platforms
- Provide comprehensive audit trails for compliance

### **7. Error Handling & Reliability**
- Automated retry mechanisms for failed API calls
- Alert generation for system failures
- Fallback mechanisms for external rate sources
- Data validation and integrity checks
- Comprehensive error logging

### **8. Reporting & Analytics**
- Rate change history reports
- Usage analytics dashboard
- Compliance reporting capabilities
- Export functionality for regulatory submissions

---

**Questions for Further Clarification:**

1. How many concurrent users do you expect the system to support?
2. What specific regulatory compliance requirements must the system meet?
3. Are there any specific rate calculation formulas or business rules that need to be implemented?
4. What is the expected data volume (number of rates, historical data retention period)?
5. Do you need any specific disaster recovery or backup requirements?

Would you like to add, modify, or remove any of these requirements? Once you confirm, we can proceed to create detailed user stories based on these finalized requirements.

```json
{
  "state": "don't change the state"
}

"""

# state_json = response.split("```json")[1].split("```")[0].strip()
# response = response.split("```json")[0].strip()


# print("state:",state_json)
