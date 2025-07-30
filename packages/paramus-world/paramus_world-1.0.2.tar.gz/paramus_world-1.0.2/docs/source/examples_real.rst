Examples with Real Data
=======================

This section provides practical examples using real data from a laboratory research environment. The examples demonstrate how to work with laboratories, scientific equipment, and researchers.

Knowledge Graph Structure
-------------------------

The examples work with this data model:

- **Laboratories**: Research facilities (Biology Lab, Chemistry Lab)
- **Lab Devices**: Scientific equipment (Microscopes, Centrifuges, HPLC systems, Spectrophotometers)
- **Researchers**: Scientists who operate the equipment (Dr. Sarah Smith)
- **Relationships**: Equipment locations, operational capabilities, maintenance status

Basic Health Check
~~~~~~~~~~~~~~~~~~

Check system status and get knowledge graph statistics:

.. code-block:: python

   from paramus_world import ParamusWorldClient

   client = ParamusWorldClient(token="your-token")
   
   health = client.check_system_health()
   print(f"System status: {health['status']}")
   print(f"Total entities: {health['world_stats']['things_count']}")
   print(f"Total triples: {health['world_stats']['triples_count']}")

**Output:**

.. code-block:: json

   {
     "status": "healthy",
     "active_sessions": 2,
     "timestamp": "2025-07-28T10:12:06.783724+00:00",
     "world_stats": {
       "things_count": 7,
       "triples_count": 56,
       "type_breakdown": {
         "LabDevice": 4,
         "Laboratory": 2,
         "Person": 1
       }
     }
   }

Laboratory Queries
------------------

Finding All Laboratories
~~~~~~~~~~~~~~~~~~~~~~~~~

Query for all laboratories with their details:

.. code-block:: python

   from paramus_world import ParamusWorldClient

   client = ParamusWorldClient(token="your-token")
   
   query = '''
   PREFIX world: <https://paramus.ai/world/>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
   PREFIX dc: <http://purl.org/dc/terms/>
   
   SELECT ?lab ?label ?description ?location ?capacity
   WHERE {
       ?lab a world:Laboratory .
       ?lab rdfs:label ?label .
       ?lab dc:description ?description .
       ?lab world:location ?location .
       ?lab world:capacity ?capacity .
   }
   '''
   
   result = client.sparql_query(query)
   print(result['result'])

**Output:**

.. code-block:: text

   lab | label | description | location | capacity
   -----------------------------------------------
   world:BiologyLab | Biology Research Lab | Main biology research laboratory for molecular studies | Building A, Floor 3 | 15
   world:ChemistryLab | Chemistry Lab | Advanced chemistry laboratory with fume hoods and analytical equipment | Building B, Floor 2 | 20

Equipment Management
--------------------

Querying Lab Devices and Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find all laboratory devices with their operational status:

.. code-block:: python

   device_query = '''
   PREFIX world: <https://paramus.ai/world/>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
   
   SELECT ?device ?label ?manufacturer ?model ?status ?lab
   WHERE {
       ?device a world:LabDevice .
       ?device rdfs:label ?label .
       ?device world:manufacturer ?manufacturer .
       ?device world:model ?model .
       ?device world:status ?status .
       ?device world:locatedIn ?lab .
   }
   ORDER BY ?status ?lab
   '''
   
   result = client.sparql_query(device_query)
   print(result['result'])

**Output:**

.. code-block:: text

   device | label | manufacturer | model | status | lab
   ----------------------------------------------------
   world:HPLC001 | HPLC System | Agilent | 1260 Infinity II | maintenance | world:ChemistryLab
   world:Microscope001 | Zeiss Confocal Microscope | Carl Zeiss | LSM 880 | operational | world:BiologyLab
   world:Centrifuge001 | High-Speed Centrifuge | Eppendorf | 5424 R | operational | world:BiologyLab
   world:Spectrophotometer001 | UV-Vis Spectrophotometer | Thermo Fisher | Evolution 220 | operational | world:ChemistryLab

Researcher Information
----------------------

Finding Researcher Capabilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query researcher information and their equipment capabilities:

.. code-block:: python

   researcher_query = '''
   PREFIX world: <https://paramus.ai/world/>
   PREFIX foaf: <http://xmlns.com/foaf/0.1/>
   PREFIX dc: <http://purl.org/dc/terms/>
   
   SELECT ?person ?name ?title ?description ?email ?device
   WHERE {
       ?person a foaf:Person .
       ?person foaf:name ?name .
       ?person foaf:title ?title .
       ?person dc:description ?description .
       ?person foaf:email ?email .
       ?person world:canOperate ?device .
   }
   '''
   
   result = client.sparql_query(researcher_query)
   print(result['result'])

**Output:**

.. code-block:: text

   person | name | title | description | email | device
   ----------------------------------------------------
   world:DrSmith | Dr. Sarah Smith | Senior Research Scientist | Lead researcher specializing in molecular biology and biochemistry | s.smith@research.org | world:Microscope001
   world:DrSmith | Dr. Sarah Smith | Senior Research Scientist | Lead researcher specializing in molecular biology and biochemistry | s.smith@research.org | world:Centrifuge001
   world:DrSmith | Dr. Sarah Smith | Senior Research Scientist | Lead researcher specializing in molecular biology and biochemistry | s.smith@research.org | world:Spectrophotometer001

Maintenance Management
----------------------

Finding Equipment Needing Maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Identify devices that require maintenance:

.. code-block:: python

   maintenance_query = '''
   PREFIX world: <https://paramus.ai/world/>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
   PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
   
   SELECT ?device ?label ?status ?maintenance_date ?lab
   WHERE {
       ?device a world:LabDevice .
       ?device rdfs:label ?label .
       ?device world:status ?status .
       ?device world:locatedIn ?lab .
       OPTIONAL { ?device world:maintenanceScheduled ?maintenance_date . }
       FILTER(?status = "maintenance" || EXISTS { ?device world:needsMaintenance "true"^^xsd:boolean })
   }
   '''
   
   result = client.sparql_query(maintenance_query)
   print(result['result'])

**Output:**

.. code-block:: text

   device | label | status | maintenance_date | lab
   ------------------------------------------------
   world:HPLC001 | HPLC System | maintenance | 2025-08-15 | world:ChemistryLab

AI Chat Integration
-------------------

Conversational Interface
~~~~~~~~~~~~~~~~~~~~~~~~

Use the AI chat feature for natural language queries:

.. code-block:: python

   # Basic greeting
   response = client.submit_chat("Hello, Paramus World! How are you today?")
   print(f"AI: {response['response']}")
   
   # Query about equipment with context
   response = client.submit_chat(
       message="What laboratory equipment is available and what's its current status?",
       context={"source": "equipment_query", "user": "researcher"}
   )
   print(f"AI: {response['response']}")

**Output:**

.. code-block:: json

   {
     "response": "Hello! I'm here to assist you with the World knowledge graph. How can I help you today?"
   }

Data Updates
------------

Adding New Equipment
~~~~~~~~~~~~~~~~~~~~

Insert new laboratory equipment into the knowledge graph:

.. code-block:: python

   update = '''
   PREFIX world: <https://paramus.ai/world/>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
   PREFIX dc: <http://purl.org/dc/terms/>
   
   INSERT DATA {
       world:NewMicroscope001 a world:LabDevice ;
           rdfs:label "Advanced Electron Microscope" ;
           dc:description "High-resolution electron microscope for nanoscale imaging" ;
           world:locatedIn world:BiologyLab ;
           world:manufacturer "JEOL" ;
           world:model "JEM-1400Plus" ;
           world:status "operational" .
           
       world:BiologyLab world:hasDevice world:NewMicroscope001 .
   }
   '''
   
   result = client.sparql_update(update)
   print(result)

**Output:**

.. code-block:: json

   {
     "message": "Update functionality to be implemented",
     "success": true
   }

Complete Laboratory Dashboard
-----------------------------

A comprehensive example combining multiple operations:

.. code-block:: python

   from paramus_world import ParamusWorldClient
   import json

   def laboratory_dashboard():
       """Complete laboratory management dashboard"""
       client = ParamusWorldClient(token="your-token")
       
       print("🔬 Laboratory Management Dashboard")
       print("=" * 40)
       
       # 1. System health check
       try:
           health = client.check_system_health()
           print(f"📊 System Status: {health['status']}")
           print(f"📈 Total Entities: {health['world_stats']['things_count']}")
           print(f"🔗 Total Relationships: {health['world_stats']['triples_count']}")
           print()
       except Exception as e:
           print(f"❌ Health check failed: {e}")
           return
       
       # 2. Laboratory overview
       lab_query = '''
       PREFIX world: <https://paramus.ai/world/>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT ?lab ?label ?capacity WHERE {
           ?lab a world:Laboratory .
           ?lab rdfs:label ?label .
           ?lab world:capacity ?capacity .
       }
       '''
       
       try:
           labs = client.sparql_query(lab_query)
           print("🏢 Laboratories:")
           print(labs['result'])
           print()
       except Exception as e:
           print(f"❌ Laboratory query failed: {e}")
       
       # 3. Equipment status summary
       status_query = '''
       PREFIX world: <https://paramus.ai/world/>
       SELECT ?status (COUNT(?device) as ?count) WHERE {
           ?device a world:LabDevice .
           ?device world:status ?status .
       }
       GROUP BY ?status
       '''
       
       try:
           status = client.sparql_query(status_query)
           print("⚙️  Equipment Status Summary:")
           print(status['result'])
           print()
       except Exception as e:
           print(f"❌ Status query failed: {e}")
       
       # 4. Maintenance alerts
       maintenance_query = '''
       PREFIX world: <https://paramus.ai/world/>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT ?device ?label ?maintenance_date WHERE {
           ?device a world:LabDevice .
           ?device rdfs:label ?label .
           ?device world:status "maintenance" .
           OPTIONAL { ?device world:maintenanceScheduled ?maintenance_date . }
       }
       '''
       
       try:
           maintenance = client.sparql_query(maintenance_query)
           print("🚨 Maintenance Required:")
           print(maintenance['result'])
           print()
       except Exception as e:
           print(f"❌ Maintenance query failed: {e}")
       
       # 5. Ask AI for insights
       try:
           ai_response = client.submit_chat(
               "Provide a summary of the current laboratory status and any recommendations.",
               context={"source": "dashboard", "type": "status_summary"}
           )
           print("🤖 AI Insights:")
           print(ai_response['response'])
       except Exception as e:
           print(f"❌ AI chat failed: {e}")

   if __name__ == "__main__":
       laboratory_dashboard()

Error Handling Best Practices
-----------------------------

Robust Query Execution
~~~~~~~~~~~~~~~~~~~~~~

Handle real-world errors and edge cases:

.. code-block:: python

   import requests
   from typing import Optional, Dict, Any

   def safe_sparql_query(client: ParamusWorldClient, 
                         query_name: str, 
                         query: str) -> Optional[Dict[str, Any]]:
       """Execute a SPARQL query with comprehensive error handling"""
       try:
           print(f"🔍 Executing {query_name}...")
           result = client.sparql_query(query)
           
           if result.get('success'):
               print(f"✅ {query_name} completed successfully")
               return result
           else:
               print(f"⚠️  {query_name} completed with issues")
               return result
               
       except requests.RequestException as e:
           print(f"❌ Network error in {query_name}: {e}")
           return None
       except ValueError as e:
           print(f"❌ API error in {query_name}: {e}")
           return None
       except Exception as e:
           print(f"❌ Unexpected error in {query_name}: {e}")
           return None

   # Usage example
   client = ParamusWorldClient(token="your-token")
   
   # Execute queries safely
   lab_data = safe_sparql_query(client, "Laboratory Query", lab_query)
   if lab_data and lab_data.get('success'):
       print("✅ Laboratory data retrieved successfully")
       print(lab_data['result'])
   else:
       print("❌ Failed to retrieve laboratory data")

Production Integration Examples
------------------------------

Flask Web API
~~~~~~~~~~~~~

Integrate with a Flask web application:

.. code-block:: python

   from flask import Flask, request, jsonify
   from paramus_world import ParamusWorldClient
   import os

   app = Flask(__name__)
   client = ParamusWorldClient(token=os.getenv("PARAMUS_TOKEN"))

   @app.route('/api/health')
   def api_health():
       """API endpoint for system health"""
       try:
           health = client.check_system_health()
           return jsonify(health)
       except Exception as e:
           return jsonify({"error": str(e)}), 500

   @app.route('/api/laboratories')
   def api_laboratories():
       """Get all laboratories"""
       query = '''
       PREFIX world: <https://paramus.ai/world/>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT ?lab ?label ?location ?capacity WHERE {
           ?lab a world:Laboratory .
           ?lab rdfs:label ?label .
           ?lab world:location ?location .
           ?lab world:capacity ?capacity .
       }
       '''
       
       try:
           result = client.sparql_query(query)
           return jsonify(result)
       except Exception as e:
           return jsonify({"error": str(e)}), 500

   @app.route('/api/equipment/<lab_id>')
   def api_equipment(lab_id):
       """Get equipment for a specific laboratory"""
       query = f'''
       PREFIX world: <https://paramus.ai/world/>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT ?device ?label ?manufacturer ?model ?status WHERE {{
           ?device a world:LabDevice .
           ?device rdfs:label ?label .
           ?device world:manufacturer ?manufacturer .
           ?device world:model ?model .
           ?device world:status ?status .
           ?device world:locatedIn world:{lab_id} .
       }}
       '''
       
       try:
           result = client.sparql_query(query)
           return jsonify(result)
       except Exception as e:
           return jsonify({"error": str(e)}), 500

   @app.route('/api/chat', methods=['POST'])
   def api_chat():
       """Chat endpoint"""
       try:
           data = request.get_json()
           message = data.get('message')
           context = data.get('context', {})
           
           response = client.submit_chat(message, context)
           return jsonify(response)
       except Exception as e:
           return jsonify({"error": str(e)}), 500

   if __name__ == '__main__':
       app.run(debug=True, port=5000)

Scheduled Monitoring
~~~~~~~~~~~~~~~~~~~

Set up automated monitoring tasks:

.. code-block:: python

   import schedule
   import time
   import smtplib
   from email.mime.text import MIMEText
   from paramus_world import ParamusWorldClient

   class LabMonitor:
       def __init__(self, token: str):
           self.client = ParamusWorldClient(token=token)
           
       def check_maintenance_alerts(self):
           """Check for equipment needing maintenance"""
           query = '''
           PREFIX world: <https://paramus.ai/world/>
           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           SELECT ?device ?label ?maintenance_date WHERE {
               ?device a world:LabDevice .
               ?device rdfs:label ?label .
               ?device world:status "maintenance" .
               OPTIONAL { ?device world:maintenanceScheduled ?maintenance_date . }
           }
           '''
           
           try:
               result = self.client.sparql_query(query)
               if result.get('success') and result['result']:
                   self.send_maintenance_alert(result['result'])
                   print(f"🚨 Maintenance alert sent: {result['result']}")
               else:
                   print("✅ All equipment operational")
           except Exception as e:
               print(f"❌ Maintenance check failed: {e}")
       
       def send_maintenance_alert(self, devices):
           """Send email alert for maintenance"""
           # Implementation depends on your email setup
           print(f"📧 Would send maintenance alert for: {devices}")
       
       def generate_daily_report(self):
           """Generate daily laboratory status report"""
           try:
               health = self.client.check_system_health()
               
               # Ask AI for summary
               ai_summary = self.client.submit_chat(
                   "Generate a daily status report for all laboratory equipment and facilities."
               )
               
               report = {
                   "date": time.strftime("%Y-%m-%d"),
                   "system_health": health,
                   "ai_summary": ai_summary['response']
               }
               
               print(f"📊 Daily report generated: {report}")
               return report
               
           except Exception as e:
               print(f"❌ Report generation failed: {e}")

   # Setup monitoring
   monitor = LabMonitor(token="your-token")

   # Schedule tasks
   schedule.every().hour.do(monitor.check_maintenance_alerts)
   schedule.every().day.at("08:00").do(monitor.generate_daily_report)

   # Run scheduler
   print("🚀 Starting laboratory monitoring system...")
   while True:
       schedule.run_pending()
       time.sleep(60)

Data Export and Analysis
~~~~~~~~~~~~~~~~~~~~~~~

Export data for external analysis:

.. code-block:: python

   import pandas as pd
   import json
   from datetime import datetime
   from paramus_world import ParamusWorldClient

   class LabDataExporter:
       def __init__(self, token: str):
           self.client = ParamusWorldClient(token=token)
       
       def export_equipment_data(self) -> pd.DataFrame:
           """Export equipment data as pandas DataFrame"""
           query = '''
           PREFIX world: <https://paramus.ai/world/>
           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           SELECT ?device ?label ?manufacturer ?model ?status ?lab WHERE {
               ?device a world:LabDevice .
               ?device rdfs:label ?label .
               ?device world:manufacturer ?manufacturer .
               ?device world:model ?model .
               ?device world:status ?status .
               ?device world:locatedIn ?lab .
           }
           '''
           
           result = self.client.sparql_query(query)
           
           # Parse result into structured data
           lines = result['result'].split('\n')[1:]  # Skip header
           data = []
           for line in lines:
               if line.strip():
                   parts = [p.strip() for p in line.split(' | ')]
                   if len(parts) == 6:
                       data.append({
                           'device': parts[0],
                           'label': parts[1],
                           'manufacturer': parts[2],
                           'model': parts[3],
                           'status': parts[4],
                           'lab': parts[5]
                       })
           
           return pd.DataFrame(data)
       
       def generate_analytics_report(self):
           """Generate comprehensive analytics report"""
           try:
               # Get equipment data
               equipment_df = self.export_equipment_data()
               
               # Basic analytics
               analytics = {
                   "timestamp": datetime.now().isoformat(),
                   "total_devices": len(equipment_df),
                   "devices_by_status": equipment_df['status'].value_counts().to_dict(),
                   "devices_by_lab": equipment_df['lab'].value_counts().to_dict(),
                   "manufacturers": equipment_df['manufacturer'].value_counts().to_dict()
               }
               
               # Export to files
               equipment_df.to_csv(f"equipment_data_{datetime.now().strftime('%Y%m%d')}.csv")
               
               with open(f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
                   json.dump(analytics, f, indent=2)
               
               print(f"📊 Analytics report generated: {analytics}")
               return analytics
               
           except Exception as e:
               print(f"❌ Analytics generation failed: {e}")
               return None

   # Usage
   exporter = LabDataExporter(token="your-token")
   analytics = exporter.generate_analytics_report()

This comprehensive set of examples demonstrates the real-world capabilities of the Paramus World Client using actual laboratory research data, showing practical applications for equipment management, researcher coordination, and facility operations.
