"""
scripts/setup_and_test.py
Script de configuração inicial e teste do módulo de IA.

Execute: python scripts/setup_and_test.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_classifier():
    print_section("1. TREINANDO CLASSIFICADOR ML")
    from classifier.ml_classifier import train, predict

    metrics = train("logreg")
    print(f"\n✅ Acurácia: {metrics['accuracy']:.2%}")

    # Testes
    test_cases = [
        ("Sua conta foi suspensa clique aqui urgente", True),
        ("Para liberar o empréstimo pague taxa de R$150", True),
        ("Reunião de equipe amanhã às 14h sala 3", False),
        ("Você ganhou iPhone clique e resgate", True),
        ("Confirme o código que chegou no seu WhatsApp", True),
    ]

    print("\nTestes de classificação:")
    for text, expected_suspicious in test_cases:
        result = predict(text)
        status = "✅" if result["is_suspicious"] == expected_suspicious else "⚠️"
        print(f"  {status} [{result['label']:20s}] ({result['confidence']:.0%}) → {text[:50]}")


def test_link_analyzer():
    print_section("2. TESTANDO ANALISADOR DE LINKS")
    from analyzer.link_analyzer import analyze_url

    urls = [
        "https://bradesc0-conta.com/login",      # phishing
        "https://bit.ly/2xKz8mQ",               # encurtador
        "http://banco-seguro.tk/verificar",      # múltiplos indicadores
        "https://www.bradesco.com.br",           # legítimo
        "https://www.google.com",               # legítimo
    ]

    for url in urls:
        r = analyze_url(url)
        icon = "🔴" if r["risk_level"] == "ALTO" else "🟡" if r["risk_level"] == "MÉDIO" else "🟢"
        print(f"  {icon} [{r['risk_level']:6s}] {url}")
        for ind in r["indicators"][:2]:
            print(f"       → {ind}")


def test_rag():
    print_section("3. CONSTRUINDO ÍNDICE RAG")
    from rag.rag_engine import get_rag

    rag = get_rag()
    print(f"\n✅ Índice construído: {rag.index.ntotal} vetores")

    queries = [
        "mensagem dizendo que conta foi bloqueada urgente",
        "promessa de rendimento garantido criptomoeda",
        "empréstimo aprovado sem consulta CPF negativado",
    ]

    print("\nTestes de recuperação RAG:")
    for query in queries:
        results = rag.retrieve(query, top_k=1)
        if results:
            r = results[0]
            print(f"\n  Query: '{query}'")
            print(f"  Fonte: {r['source']} (score: {r['score']:.3f})")
            print(f"  Trecho: {r['chunk'][:120]}...")


def test_sabia():
    print_section("4. TESTANDO INTEGRAÇÃO COM SABIÁ (Maritaca AI)")

    api_key = os.getenv("MARITACA_API_KEY", "")
    if not api_key or api_key == "your_maritaca_api_key_here":
        print("\n⚠️  MARITACA_API_KEY não configurada.")
        print("   Para testar o Sabiá:")
        print("   1. Acesse https://plataforma.maritaca.ai")
        print("   2. Crie uma conta gratuita")
        print("   3. Gere sua API key")
        print("   4. Adicione no arquivo .env: MARITACA_API_KEY=sua_chave")
        print("\n   A API tem uso gratuito para desenvolvimento!")
        return

    from rag.sabia_client import analyze_with_rag
    from rag.rag_engine import get_rag

    text = "Olá! Identificamos uma tentativa de fraude na sua conta. Para proteger seu dinheiro, faça um PIX de R$500 para nossa conta segura temporária. Você receberá o estorno em 24h."

    rag = get_rag()
    context = rag.build_context(text)
    result = analyze_with_rag(text, context)

    print(f"\n  Texto analisado: {text[:80]}...")
    print(f"  ➡️  Tipo: {result.get('fraud_type')}")
    print(f"  ➡️  Risco: {result.get('risk_level')}")
    print(f"  ➡️  Confiança: {result.get('confidence', 0):.0%}")
    print(f"  ➡️  Explicação: {result.get('explanation', '')[:200]}")
    print("\n✅ Sabiá integrado com sucesso!")


def test_full_pipeline():
    print_section("5. PIPELINE COMPLETO (sem Sabiá)")
    from analyzer.detection_service import analyze_content

    test_texts = [
        "Parabéns! Você foi sorteado. Clique http://bit.ly/premio-falso para resgatar seu iPhone.",
        "Reunião de projeto dIscovery amanhã às 10h sala de reuniões.",
        "Para liberar seu empréstimo de R$5000, pague taxa de R$89 de seguro por PIX.",
    ]

    for text in test_texts:
        result = analyze_content(text, use_sabia=False)
        icon = "🔴" if result["is_suspicious"] else "🟢"
        print(f"\n  {icon} Risco: {result['risk_level']} | Tipo: {result['fraud_type']}")
        print(f"     Texto: {text[:70]}...")
        print(f"     Tempo: {result['analysis_time_ms']}ms")


if __name__ == "__main__":
    print("\n🔍 dIscovery AI - Setup & Test")
    print("Verificando módulos...\n")

    try:
        test_classifier()
        test_link_analyzer()
        test_rag()
        test_sabia()
        test_full_pipeline()

        print_section("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("\nPróximos passos:")
        print("  1. Configure MARITACA_API_KEY no .env")
        print("  2. Execute a API: cd api && python main.py")
        print("  3. Acesse a documentação: http://localhost:8000/docs")
        print("  4. Teste via curl:")
        print('     curl -X POST http://localhost:8000/api/analyze \\')
        print('       -H "Content-Type: application/json" \\')
        print('       -d \'{"text": "Sua conta foi bloqueada clique aqui", "use_sabia": false}\'')

    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
