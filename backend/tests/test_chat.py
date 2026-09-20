from starlette.testclient import TestClient


def test_chat_query_and_persistence(client: TestClient):
    """Verifies that asking a question creates Conversation, Message, and persists them."""
    # 1. Post a query
    res = client.post(
        "/api/v1/chat/query",
        json={"message": "What is the procedure for handling temperature excursions?"},
    )
    assert res.status_code == 200
    data = res.json()

    assert "conversation_id" in data
    assert "user_message_id" in data
    assert "assistant_message_id" in data
    assert data["policy_applied"] == "Grounded Answering Policy"
    assert data["is_grounded"] is True
    assert isinstance(data["citations"], list)
    conv_id = data["conversation_id"]
    asst_msg_id = data["assistant_message_id"]

    # 2. Check conversation listing persistence
    list_res = client.get("/api/v1/chat/conversations")
    assert list_res.status_code == 200
    conv_list = list_res.json()
    assert any(c["id"] == conv_id for c in conv_list)

    # 3. Check detailed conversation retrieval with messages
    detail_res = client.get(f"/api/v1/chat/conversations/{conv_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == conv_id
    assert len(detail["messages"]) >= 2
    # First is USER, second is ASSISTANT
    assert detail["messages"][0]["sender_type"] == "USER"
    assert detail["messages"][1]["sender_type"] == "ASSISTANT"

    # 4. Check feedback submission and persistence
    feedback_res = client.post(
        "/api/v1/chat/feedback",
        json={
            "message_id": asst_msg_id,
            "rating": 1,
            "category": "ACCURACY",
            "comments": "Exact SOP citation provided.",
        },
    )
    assert feedback_res.status_code == 201
    fb_data = feedback_res.json()
    assert fb_data["message_id"] == asst_msg_id
    assert fb_data["status"] == "RECORDED"


def test_hybrid_search_endpoint(client: TestClient):
    """Verifies direct hybrid search endpoint."""
    res = client.get("/api/v1/search?query=temperature+cold+chain")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "total_results" in data
    assert "latency_ms" in data
    assert data["query"] == "temperature cold chain"
