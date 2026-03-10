from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Whyh3ll0th3r31!")

driver = GraphDatabase.driver(URI, auth=AUTH)
import os

with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    session.run("""
        CREATE CONSTRAINT person_name IF NOT EXISTS
        FOR (n:Person) REQUIRE n.name IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT account_id IF NOT EXISTS
        FOR (n:Account) REQUIRE n.id IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT device_id IF NOT EXISTS
        FOR (n:Device) REQUIRE n.id IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT credential_id IF NOT EXISTS
        FOR (n:Credential) REQUIRE n.id IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT incident_id IF NOT EXISTS
        FOR (n:Incident) REQUIRE n.id IS UNIQUE
    """)

    session.run("""
        CREATE CONSTRAINT event_id IF NOT EXISTS
        FOR (n:Event) REQUIRE n.id IS UNIQUE
    """)

    session.run("""
        MERGE (incident:Incident {
            id: "INC-001",
            type: "SIM Re-provisioning Fraud",
            summary: "Victim's phone number was re-provisioned to a replacement SIM without authorization, enabling interception of SMS one-time passcodes."
        })

        MERGE (officers:Organization {
            name: "Attending Officers",
            type: "Law Enforcement"
        })

        MERGE (fraudTeam:Organization {
            name: "Mobile Network Fraud Team",
            type: "Telecom Fraud Team"
        })

        MERGE (carrier:Organization {
            name: "Carrier",
            type: "Mobile Network Operator"
        })

        MERGE (victim:Person {
            name: "Victim"
        })

        MERGE (employee:Person {
            name: "Unknown Employee"
        })

        MERGE (cred:Credential {
            id: "employee-credential-001",
            type: "Employee Credential"
        })

        MERGE (phoneNumber:Identifier {
            value: "Victim Phone Number",
            type: "MSISDN"
        })

        MERGE (msisdn:Identifier {
            value: "Victim MSISDN",
            type: "MSISDN"
        })

        MERGE (imsi:Identifier {
            value: "Victim IMSI Mapping",
            type: "IMSI"
        })

        MERGE (originalHandset:Device {
            id: "device-handset-001",
            type: "Handset"
        })

        MERGE (replacementSim:Device {
            id: "device-sim-002",
            type: "Replacement SIM"
        })

        MERGE (carrierProvisioning:System {
            name: "Carrier Provisioning Interface",
            type: "Provisioning Interface"
        })

        MERGE (vpnGateway:System {
            name: "Legacy VPN Gateway",
            type: "VPN Gateway"
        })

        MERGE (auditLogs:DataStore {
            name: "Internal Audit Logs",
            type: "Audit Log"
        })

        MERGE (bankingAccount:Account {
            id: "banking-login-001",
            type: "Banking Login"
        })

        MERGE (otp:Data {
            id: "sms-otp-001",
            type: "SMS One-Time Passcode"
        })

        MERGE (officers)-[:WERE_INFORMED_BY]->(fraudTeam)
        MERGE (fraudTeam)-[:REPORTED_INCIDENT]->(incident)

        MERGE (incident)-[:HAS_VICTIM]->(victim)
        MERGE (victim)-[:OWNS]->(phoneNumber)
        MERGE (victim)-[:ASSOCIATED_WITH]->(msisdn)
        MERGE (victim)-[:USES]->(originalHandset)
        MERGE (victim)-[:HAS_ACCOUNT]->(bankingAccount)

        MERGE (phoneNumber)-[:REPROVISIONED_TO]->(replacementSim)
        MERGE (msisdn)-[:ASSOCIATED_WITH]->(imsi)

        MERGE (employee)-[:USES]->(cred)
        MERGE (cred)-[:ACCESSED_VIA]->(vpnGateway)
        MERGE (cred)-[:ACCESSED]->(carrierProvisioning)
        MERGE (auditLogs)-[:RECORDED_ACCESS_BY]->(cred)

        MERGE (cred)-[:MODIFIED]->(imsi)
        MERGE (carrierProvisioning)-[:MANAGES]->(imsi)
        MERGE (carrier)-[:OPERATES]->(carrierProvisioning)
        MERGE (carrier)-[:MAINTAINS]->(auditLogs)

        MERGE (otp)-[:USED_FOR]->(bankingAccount)
        MERGE (otp)-[:RECEIVED_ON]->(replacementSim)

        MERGE (incident)-[:INVOLVES_SYSTEM]->(carrierProvisioning)
        MERGE (incident)-[:INVOLVES_SYSTEM]->(vpnGateway)
        MERGE (incident)-[:INVOLVES_DATA]->(otp)
        MERGE (incident)-[:INVOLVES_CREDENTIAL]->(cred)

        MERGE (incident)-[:NO_PHYSICAL_THEFT_OF]->(originalHandset)

        MERGE (e1:Event {
            id: "EVT-001",
            type: "Notification",
            description: "Attending officers informed by mobile network fraud team"
        })
        MERGE (e2:Event {
            id: "EVT-002",
            type: "Access",
            description: "Employee credential accessed carrier provisioning interface via legacy VPN gateway"
        })
        MERGE (e3:Event {
            id: "EVT-003",
            type: "Modification",
            description: "IMSI mapping associated with victim's MSISDN modified"
        })
        MERGE (e4:Event {
            id: "EVT-004",
            type: "Reprovisioning",
            description: "Victim's phone number re-provisioned to replacement SIM without request"
        })
        MERGE (e5:Event {
            id: "EVT-005",
            type: "Interception",
            description: "SMS one-time passcodes received on substituted SIM"
        })
        MERGE (e6:Event {
            id: "EVT-006",
            type: "Observation",
            description: "No physical theft of handset occurred"
        })

        MERGE (incident)-[:HAS_EVENT]->(e1)
        MERGE (incident)-[:HAS_EVENT]->(e2)
        MERGE (incident)-[:HAS_EVENT]->(e3)
        MERGE (incident)-[:HAS_EVENT]->(e4)
        MERGE (incident)-[:HAS_EVENT]->(e5)
        MERGE (incident)-[:HAS_EVENT]->(e6)

        MERGE (e1)-[:NEXT]->(e2)
        MERGE (e2)-[:NEXT]->(e3)
        MERGE (e3)-[:NEXT]->(e4)
        MERGE (e4)-[:NEXT]->(e5)
        MERGE (e5)-[:NEXT]->(e6)

        MERGE (e1)-[:ACTOR]->(fraudTeam)
        MERGE (e1)-[:TARGET]->(officers)

        MERGE (e2)-[:ACTOR]->(cred)
        MERGE (e2)-[:VIA]->(vpnGateway)
        MERGE (e2)-[:TARGET]->(carrierProvisioning)

        MERGE (e3)-[:ACTOR]->(cred)
        MERGE (e3)-[:TARGET]->(imsi)
        MERGE (e3)-[:RELATES_TO]->(msisdn)

        MERGE (e4)-[:TARGET]->(phoneNumber)
        MERGE (e4)-[:RESULTED_IN]->(replacementSim)
        MERGE (e4)-[:AFFECTED]->(victim)

        MERGE (e5)-[:TARGET]->(otp)
        MERGE (e5)-[:RESULTED_IN]->(replacementSim)
        MERGE (e5)-[:RELATES_TO]->(bankingAccount)

        MERGE (e6)-[:TARGET]->(originalHandset)
    """)

    # result = session.run("""
    #     MATCH (a:object)-[:RE_PROVISIONED]->(b:object)
    #     RETURN a.name AS a, b.name AS b
    # """)

    # for record in result:
    #     print(record["a"], "knows", record["b"])

driver.close()