import asyncio
from app.rag.retrieval import HybridRetriever
from app.auth.context import UserContext
from app.db.session import get_session_factory

async def main():
    retriever = HybridRetriever(top_k=6)
    u = UserContext(
        user_id="test",
        email="test@acme.com",
        workspace_id="00000000-0000-0000-0000-000000000001",
        department_id="quality_assurance",
        roles=["ADMIN"],
        access_level=1,
    )
    sf = get_session_factory()
    async with sf() as session:
        query = "What is the time limit for reporting a major deviation?"
        res = await retriever.retrieve(query, u, session)
        print(f"Results for '{query}':")
        for i, c in enumerate(res.chunks):
            print(f"Rank {i}: Doc={c.document_title}, P={c.page_number}, Sec={c.section_heading}, RRF={c.rrf_score:.4f}, Dense={c.dense_score:.4f}, Sparse={c.sparse_score:.4f}")
            print(f"Snippet: {c.content[:200]}\n---")

if __name__ == "__main__":
    asyncio.run(main())
