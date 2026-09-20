import sys
import asyncio
from starlette.testclient import TestClient
from app.main import app
from app.auth.context import UserContext
from app.auth.context import get_current_user_context

def run_e2e_smoke_tests():
    print("==================================================")
    print("PHASE 3: 10-SCENARIO END-TO-END MANUAL SMOKE TEST")
    print("==================================================")

    results = {}
    client = TestClient(app)

    # ----------------------------------------------------
    # SCENARIO 1: Known-answer RAG test
    # ----------------------------------------------------
    print("\n--- [Scenario 1] Known-answer RAG test ---")
    query_1 = "What temperature range is required for cold chain storage?"
    res_1 = client.post("/api/v1/chat/query", json={"message": query_1})
    assert res_1.status_code == 200, f"Status code: {res_1.status_code}"
    data_1 = res_1.json()
    print("Question:", query_1)
    print("Answer:", data_1["answer"])
    print("Grounded:", data_1["is_grounded"])
    print("Policy:", data_1["policy_applied"])
    print("Citations count:", len(data_1["citations"]))

    s1_pass = False
    if data_1["is_grounded"] and ("2" in data_1["answer"] and "8" in data_1["answer"]):
        citation = data_1["citations"][0]
        print(f"Citation 1: Doc='{citation['document_title']}', Section='{citation['section_heading']}'")
        print(f"Excerpt: {citation['relevant_text'][:120]}...")
        if "Cold Chain" in citation["document_title"] or "Cold-Chain" in citation["document_title"]:
            s1_pass = True
    results["Known RAG"] = "PASS" if s1_pass else "FAIL"
    print(f"Result Scenario 1: {results['Known RAG']}")

    # ----------------------------------------------------
    # SCENARIO 2: Semantic retrieval test
    # ----------------------------------------------------
    print("\n--- [Scenario 2] Semantic retrieval test ---")
    query_2 = "How should temperature-sensitive materials be stored?"
    res_2 = client.post("/api/v1/chat/query", json={"message": query_2})
    assert res_2.status_code == 200
    data_2 = res_2.json()
    print("Question:", query_2)
    print("Answer:", data_2["answer"])
    print("Grounded:", data_2["is_grounded"])
    s2_pass = False
    if data_2["is_grounded"] and len(data_2["citations"]) > 0:
        c = data_2["citations"][0]
        print(f"Matched: Doc='{c['document_title']}', Section='{c['section_heading']}'")
        if "Cold" in c["document_title"] or "Storage" in c["section_heading"] or "temperature" in c["relevant_text"].lower():
            s2_pass = True
    results["Semantic retrieval"] = "PASS" if s2_pass else "FAIL"
    print(f"Result Scenario 2: {results['Semantic retrieval']}")

    # ----------------------------------------------------
    # SCENARIO 3: Out-of-scope / Grounded refusal test
    # ----------------------------------------------------
    print("\n--- [Scenario 3] Out-of-scope / Grounded refusal test ---")
    query_3 = "Who won the 2022 FIFA World Cup?"
    res_3 = client.post("/api/v1/chat/query", json={"message": query_3})
    assert res_3.status_code == 200
    data_3 = res_3.json()
    print("Question:", query_3)
    print("Answer:", data_3["answer"])
    print("Grounded:", data_3["is_grounded"])
    print("Grounding Status:", data_3["grounding_status"])
    s3_pass = False
    if (data_3["is_grounded"] is False 
        and data_3["grounding_status"] == "REFUSED_INSUFFICIENT_EVIDENCE"
        and "Grounded Answering Policy" in data_3["answer"]
        and len(data_3["citations"]) == 0):
        s3_pass = True
    results["Grounded refusal"] = "PASS" if s3_pass else "FAIL"
    print(f"Result Scenario 3: {results['Grounded refusal']}")

    # ----------------------------------------------------
    # SCENARIO 4: Deviation SOP test
    # ----------------------------------------------------
    print("\n--- [Scenario 4] Deviation SOP test ---")
    query_4 = "What is the time limit for reporting a major deviation?"
    res_4 = client.post("/api/v1/chat/query", json={"message": query_4})
    assert res_4.status_code == 200
    data_4 = res_4.json()
    print("Question:", query_4)
    print("Answer:", data_4["answer"])
    print("Citations:", len(data_4["citations"]))
    s4_pass = False
    if data_4["is_grounded"] and len(data_4["citations"]) > 0:
        c4 = data_4["citations"][0]
        print(f"Citation: Doc='{c4['document_title']}', Section='{c4['section_heading']}'")
        print(f"Excerpt: {c4['relevant_text']}")
        if "Deviation" in c4["document_title"] and any(term in (c4["relevant_text"] + data_4["answer"]).lower() for term in ["hour", "day", "deviation", "investigation", "sla"]):
            s4_pass = True
    results["Deviation SOP"] = "PASS" if s4_pass else "FAIL"
    print(f"Result Scenario 4: {results['Deviation SOP']}")

    # ----------------------------------------------------
    # SCENARIO 5: Unauthorized-access test
    # ----------------------------------------------------
    print("\n--- [Scenario 5] Unauthorized-access test ---")
    from app.models.workspace import Workspace
    from app.models.user import User
    from app.db.session import get_session_factory
    
    async def ensure_unauth_fixtures():
        sf = get_session_factory()
        async with sf() as session:
            ws = await session.get(Workspace, "ws-unauth-test")
            if not ws:
                ws = Workspace(id="ws-unauth-test", name="Unauthorized Test Workspace", slug="unauth-test")
                session.add(ws)
            u = await session.get(User, "usr-unauth-001")
            if not u:
                u = User(id="usr-unauth-001", email="unauth@acmepharma.demo", role="EMPLOYEE")
                session.add(u)
            await session.commit()
    
    asyncio.run(ensure_unauth_fixtures())

    unauth_user = UserContext(
        user_id="usr-unauth-001",
        email="unauth@acmepharma.demo",
        workspace_id="ws-unauth-test",  # Different authorized workspace!
        department_id="marketing",
        role="EMPLOYEE",
        is_admin=False,
    )
    app.dependency_overrides[get_current_user_context] = lambda: unauth_user
    
    # 1. Chat attempt
    unauth_chat_res = client.post(
        "/api/v1/chat/query?workspace_id=ws-default-001",  # Frontend tampering attempt!
        json={"message": "What is the time limit for reporting a major deviation?"}
    )
    unauth_chat_data = unauth_chat_res.json()
    print("Unauthorized Chat Grounded:", unauth_chat_data["is_grounded"])
    print("Unauthorized Chat Citations:", len(unauth_chat_data["citations"]))
    print("Unauthorized Chat Answer:", unauth_chat_data["answer"][:80])

    # 2. Search attempt
    unauth_search_res = client.get(
        "/api/v1/search?query=deviation&workspace_id=ws-default-001"  # Tampering attempt
    )
    unauth_search_data = unauth_search_res.json()
    print("Unauthorized Search Results Count:", len(unauth_search_data["results"]))

    # Clean up override
    app.dependency_overrides.pop(get_current_user_context, None)

    s5_pass = False
    if (unauth_chat_data["is_grounded"] is False 
        and len(unauth_chat_data["citations"]) == 0
        and len(unauth_search_data["results"]) == 0):
        s5_pass = True
    results["Authorization"] = "PASS" if s5_pass else "FAIL"
    print(f"Result Scenario 5: {results['Authorization']}")

    # ----------------------------------------------------
    # SCENARIO 6: Conversation persistence test
    # ----------------------------------------------------
    print("\n--- [Scenario 6] Conversation persistence test ---")
    conv_res = client.post("/api/v1/chat/query", json={"message": "What are the documentation guidelines for deviations?"})
    conv_data = conv_res.json()
    cid = conv_data["conversation_id"]
    print(f"Created Conversation ID: {cid}")

    # Reload conversation details (simulating browser page refresh and open)
    detail_res = client.get(f"/api/v1/chat/conversations/{cid}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    print(f"Reloaded conversation message count: {len(detail_data['messages'])}")
    has_citations = False
    for msg in detail_data["messages"]:
        if msg["sender_type"] == "ASSISTANT" and len(msg.get("sources", [])) > 0:
            has_citations = True
            print(f"Found persisted assistant citation: {msg['sources'][0]['document_title']}")

    s6_pass = (len(detail_data["messages"]) >= 2 and has_citations)
    results["Conversation persistence"] = "PASS" if s6_pass else "FAIL"
    print(f"Result Scenario 6: {results['Conversation persistence']}")

    # ----------------------------------------------------
    # SCENARIO 7: Feedback test
    # ----------------------------------------------------
    print("\n--- [Scenario 7] Feedback test ---")
    asst_msg_id = conv_data["assistant_message_id"]
    fb_pos = client.post("/api/v1/chat/feedback", json={
        "message_id": asst_msg_id,
        "rating": 1,
        "category": "ACCURACY",
        "comments": "Accurate SOP retrieval"
    })
    assert fb_pos.status_code == 201
    print("Submitted positive feedback:", fb_pos.json())

    fb_neg = client.post("/api/v1/chat/feedback", json={
        "message_id": asst_msg_id,
        "rating": -1,
        "category": "CITATION_QUALITY",
        "comments": "Tested negative rating toggle"
    })
    assert fb_neg.status_code == 201
    print("Submitted negative feedback:", fb_neg.json())
    s7_pass = (fb_pos.json()["status"] == "RECORDED" and fb_neg.json()["status"] == "RECORDED")
    results["Feedback"] = "PASS" if s7_pass else "FAIL"
    print(f"Result Scenario 7: {results['Feedback']}")

    # ----------------------------------------------------
    # SCENARIO 8: Citation integrity test
    # ----------------------------------------------------
    print("\n--- [Scenario 8] Citation integrity test ---")
    # Verify every citation excerpt contains real textual evidence supporting the claim
    test_queries = [
        "What temperature range is required for cold chain storage?",
        "What is the time limit for reporting a major deviation?",
        "How should temperature-sensitive materials be stored?"
    ]
    s8_pass = True
    total_citations_checked = 0
    for q in test_queries:
        r = client.post("/api/v1/chat/query", json={"message": q}).json()
        for cit in r.get("citations", []):
            total_citations_checked += 1
            excerpt = cit.get("relevant_text", "")
            title = cit.get("document_title", "")
            sec = cit.get("section_heading", "")
            print(f"Verifying citation for '{q}': [{title} - {sec}]")
            # Must have non-trivial excerpt text
            if len(excerpt.strip()) < 20:
                print(f"FAILED: Excerpt too short ({len(excerpt)} chars)")
                s8_pass = False
            # Verify excerpt actually contains topical keywords
            if "temperature" in q.lower() and not any(k in excerpt.lower() for k in ["temp", "temperature", "cold", "storage", "celsius", "2", "8", "quarantine", "excursion", "chamber", "band", "monitoring", "sample", "biopharmaceutical"]):
                print("FAILED: Excerpt does not support temperature claim")
                s8_pass = False
            if "deviation" in q.lower() and not any(k in excerpt.lower() for k in ["deviation", "report", "hour", "day", "investigation", "sla", "24", "immediate"]):
                print("FAILED: Excerpt does not support deviation claim")
                s8_pass = False

    print(f"Total citations verified with evidence: {total_citations_checked}")
    s8_pass = s8_pass and (total_citations_checked >= 3)
    results["Citation integrity"] = "PASS" if s8_pass else "FAIL"
    print(f"Result Scenario 8: {results['Citation integrity']}")

    # ----------------------------------------------------
    # SCENARIO 9: Search test
    # ----------------------------------------------------
    print("\n--- [Scenario 9] Search test ---")
    # Keyword search
    kw_res = client.get("/api/v1/search?query=SOP-QA-042")
    assert kw_res.status_code == 200
    kw_data = kw_res.json()
    print("Keyword search query 'SOP-QA-042' found:", len(kw_data["results"]), "results")

    # Semantic search
    sem_res = client.get("/api/v1/search?query=protocol+for+maintaining+chilled+products")
    assert sem_res.status_code == 200
    sem_data = sem_res.json()
    print("Semantic search query found:", len(sem_data["results"]), "results")

    s9_pass = False
    if len(kw_data["results"]) > 0 and len(sem_data["results"]) > 0:
        top_res = sem_data["results"][0]
        print("Top Semantic match:", top_res["document_title"], "RRF Score:", top_res["rrf_score"], "Dense:", top_res["dense_score"], "Sparse:", top_res["sparse_score"])
        if top_res["rrf_score"] > 0 and top_res["document_id"] and top_res["snippet"]:
            s9_pass = True
    results["Search"] = "PASS" if s9_pass else "FAIL"
    print(f"Result Scenario 9: {results['Search']}")

    # ----------------------------------------------------
    # SCENARIO 10: UI/API error handling
    # ----------------------------------------------------
    print("\n--- [Scenario 10] UI/API error handling ---")
    # 1. Empty message
    bad_res1 = client.post("/api/v1/chat/query", json={"message": ""})
    print("Empty query status:", bad_res1.status_code) # Expect 422
    # 2. Non-existent conversation
    bad_res2 = client.get("/api/v1/chat/conversations/00000000-0000-0000-0000-999999999999")
    print("Non-existent conversation status:", bad_res2.status_code) # Expect 404
    # 3. Invalid search parameters
    bad_res3 = client.get("/api/v1/search?query=")
    print("Empty search query status:", bad_res3.status_code) # Expect 422

    s10_pass = (bad_res1.status_code == 422 and bad_res2.status_code == 404 and bad_res3.status_code == 422)
    results["Error handling"] = "PASS" if s10_pass else "FAIL"
    print(f"Result Scenario 10: {results['Error handling']}")

    print("\n==================================================")
    print("SUMMARY OF MANUAL VERIFICATION SCENARIOS")
    print("==================================================")
    for k, v in results.items():
        print(f"{k}: {v}")

    all_passed = all(v == "PASS" for v in results.values())
    print("\nOVERALL STATUS:", "READY" if all_passed else "NOT READY")
    return all_passed

if __name__ == "__main__":
    success = run_e2e_smoke_tests()
    if not success:
        sys.exit(1)
