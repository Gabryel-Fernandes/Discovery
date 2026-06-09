"""
scripts/evaluation_report.py
Gera relatório completo de acurácia do classificador ML.

Métricas geradas:
- Acurácia geral
- Precision, Recall, F1 por classe
- Matriz de confusão
- Falsos positivos e falsos negativos detalhados
- Relatório salvo em data/evaluation_report.json e data/evaluation_report.txt

Uso:
    python scripts/evaluation_report.py
    python scripts/evaluation_report.py --model naive_bayes
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
import numpy as np

from classifier.ml_classifier import (
    TRAINING_DATA,
    build_pipeline,
    preprocess_text,
    train,
)


OUTPUT_DIR = Path("./data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── CONJUNTO DE TESTE MANUAL (gabarito humano) ────────────────────────────────
# Textos reais coletados para validação. Cada entrada tem:
# text, expected_label, expected_suspicious, source (de onde veio o exemplo)

MANUAL_TEST_SET = [
    # Golpes confirmados
    ("Sua conta Nubank foi suspensa clique aqui para reativar urgente", "phishing", True, "simulado"),
    ("Transferi por PIX para conta errada quero estorno ligue agora", "golpe_pix", True, "simulado"),
    ("Empréstimo aprovado CPF negativado pague taxa liberação R$89", "falso_emprestimo", True, "simulado"),
    ("Parabéns você ganhou iPhone 15 clique para resgatar hoje", "falsa_promocao", True, "simulado"),
    ("Chaveiro 24h abertura carro R$40 pago por PIX", "falso_servico", True, "simulado"),
    ("Rendimento garantido 20% mês grupo VIP telegram crypto", "falso_investimento", True, "simulado"),
    ("Sou do banco preciso código SMS para cancelar transação", "engenharia_social", True, "simulado"),
    ("Oi mãe mudei número pode me fazer PIX urgente R$300", "clonagem_conta", True, "simulado"),
    ("Vírus detectado dispositivo ligue suporte Microsoft agora", "golpe_suporte_tecnico", True, "simulado"),
    ("QR code enviado WhatsApp para pagar taxa entrega retida", "golpe_qr_code", True, "simulado"),
    ("Produto retido alfândega pague taxa R$50 para liberar", "golpe_delivery", True, "simulado"),
    # Legítimos confirmados (incluindo os que falhavam antes)
    ("Nubank buscador boletos encontrou novo boleto no seu CPF emitido por assistência saúde agende pagamento", "legitimo", False, "email_real_nubank"),
    ("Uber e Nubank clientes têm 50% de desconto na próxima viagem pague com NuPay ou cartão Nubank", "legitimo", False, "email_real_uber"),
    ("Apple dia das mães frete grátis comprar iPhone 17 parcelado política privacidade minha conta apple", "legitimo", False, "email_real_apple"),
    ("Seu pedido foi enviado código rastreamento transportadora previsão chegada 3 dias úteis", "legitimo", False, "email_real_ecommerce"),
    ("Reunião de equipe amanhã às 14h sala de conferência pauta enviada por email", "legitimo", False, "mensagem_corporativa"),
    ("Spotify sua assinatura foi renovada com sucesso próxima cobrança gerenciar plano", "legitimo", False, "email_real_spotify"),
    ("Google sua senha foi alterada dispositivo Android segurança atividade conta verificar sou eu", "legitimo", False, "email_real_google"),
    ("Receita Federal consulta CPF situação regular sem pendências declaração entregue recibo", "legitimo", False, "email_real_receita"),
]


def run_evaluation(model_type: str = "logreg") -> dict:
    print(f"\n{'='*60}")
    print(f"  dIscovery AI — Relatório de Avaliação do Classificador")
    print(f"  Modelo: {model_type} | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}\n")

    texts = [d[0] for d in TRAINING_DATA]
    labels = [d[1] for d in TRAINING_DATA]

    # ── 1. Treino e avaliação com hold-out 15% ─────────────────────────────
    print("► Treinando modelo...")
    metrics = train(model_type)
    pipeline = build_pipeline(model_type)
    pipeline.fit(texts, labels)

    # ── 2. Cross-validation 5-fold ─────────────────────────────────────────
    print("\n► Rodando cross-validation 5-fold...")
    try:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(pipeline, texts, labels, cv=cv, scoring="f1_weighted")
        cv_mean = float(cv_scores.mean())
        cv_std = float(cv_scores.std())
        print(f"  F1 médio (5-fold): {cv_mean:.2%} ± {cv_std:.2%}")
    except Exception as e:
        cv_mean, cv_std = 0.0, 0.0
        print(f"  Cross-validation falhou: {e}")

    # ── 3. Teste no conjunto manual (gabarito humano) ──────────────────────
    print("\n► Avaliando conjunto de teste manual (gabarito humano)...")
    manual_texts = [t[0] for t in MANUAL_TEST_SET]
    manual_labels = [t[1] for t in MANUAL_TEST_SET]
    manual_sources = [t[3] for t in MANUAL_TEST_SET]

    pipeline_trained = build_pipeline(model_type)
    pipeline_trained.fit(texts, labels)
    manual_preds = pipeline_trained.predict(manual_texts)
    manual_probas = pipeline_trained.predict_proba(manual_texts)
    manual_classes = pipeline_trained.classes_

    manual_acc = accuracy_score(manual_labels, manual_preds)
    manual_report = classification_report(manual_labels, manual_preds, output_dict=True, zero_division=0)

    print(f"\n  Acurácia no conjunto manual: {manual_acc:.2%}")
    print(f"\n{classification_report(manual_labels, manual_preds, zero_division=0)}")

    # ── 4. Análise de erros ────────────────────────────────────────────────
    errors = []
    false_positives = []  # legítimo classificado como golpe
    false_negatives = []  # golpe classificado como legítimo

    for i, (text, true_label, pred_label, source) in enumerate(
        zip(manual_texts, manual_labels, manual_preds, manual_sources)
    ):
        if true_label != pred_label:
            entry = {
                "text": text[:100],
                "expected": true_label,
                "predicted": pred_label,
                "source": source,
                "confidence": float(max(manual_probas[i])),
            }
            errors.append(entry)
            if true_label == "legitimo":
                false_positives.append(entry)
            elif pred_label == "legitimo":
                false_negatives.append(entry)

    print(f"\n  ✅ Acertos: {len(manual_texts) - len(errors)}/{len(manual_texts)}")
    print(f"  ❌ Erros totais: {len(errors)}")
    print(f"  🔴 Falsos positivos (legítimo → golpe): {len(false_positives)}")
    print(f"  🟡 Falsos negativos (golpe → legítimo): {len(false_negatives)}")

    if false_positives:
        print("\n  Falsos positivos detectados:")
        for fp in false_positives:
            print(f"    - [{fp['predicted']}] '{fp['text'][:60]}...' (fonte: {fp['source']})")

    if false_negatives:
        print("\n  Falsos negativos detectados:")
        for fn in false_negatives:
            print(f"    - [{fn['expected']}] '{fn['text'][:60]}...' (fonte: {fn['source']})")

    # ── 5. Métricas por classe ─────────────────────────────────────────────
    print("\n► Métricas por classe (conjunto de treino + hold-out):")
    all_labels_set = sorted(set(labels))
    pipeline_full = build_pipeline(model_type)

    from sklearn.model_selection import train_test_split
    X_tr, X_te, y_tr, y_te = train_test_split(texts, labels, test_size=0.15, random_state=42)
    pipeline_full.fit(X_tr, y_tr)
    y_pred_te = pipeline_full.predict(X_te)

    per_class = {}
    report_dict = classification_report(y_te, y_pred_te, output_dict=True, zero_division=0)
    for cls in all_labels_set:
        if cls in report_dict:
            per_class[cls] = {
                "precision": round(report_dict[cls]["precision"], 3),
                "recall": round(report_dict[cls]["recall"], 3),
                "f1": round(report_dict[cls]["f1-score"], 3),
                "support": report_dict[cls]["support"],
            }

    # ── 6. Monta relatório final ───────────────────────────────────────────
    report = {
        "generated_at": datetime.now().isoformat(),
        "model_type": model_type,
        "training_samples": len(texts),
        "classes": all_labels_set,
        "holdout_evaluation": {
            "accuracy": metrics["accuracy"],
            "n_test": metrics["n_test"],
        },
        "cross_validation": {
            "folds": 5,
            "f1_weighted_mean": round(cv_mean, 4),
            "f1_weighted_std": round(cv_std, 4),
        },
        "manual_test_set": {
            "total": len(manual_texts),
            "accuracy": round(manual_acc, 4),
            "errors": len(errors),
            "false_positives": len(false_positives),
            "false_negatives": len(false_negatives),
            "error_details": errors,
        },
        "per_class_metrics": per_class,
        "overall": {
            "macro_f1": round(report_dict.get("macro avg", {}).get("f1-score", 0), 4),
            "weighted_f1": round(report_dict.get("weighted avg", {}).get("f1-score", 0), 4),
        },
    }

    # ── 7. Salva relatório ─────────────────────────────────────────────────
    json_path = OUTPUT_DIR / "evaluation_report.json"
    txt_path = OUTPUT_DIR / "evaluation_report.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"dIscovery AI — Relatório de Avaliação\n")
        f.write(f"Gerado em: {report['generated_at']}\n")
        f.write(f"Modelo: {model_type}\n\n")
        f.write(f"Amostras de treino: {len(texts)}\n")
        f.write(f"Acurácia (hold-out 15%): {metrics['accuracy']:.2%}\n")
        f.write(f"F1 cross-validation (5-fold): {cv_mean:.2%} ± {cv_std:.2%}\n\n")
        f.write(f"Conjunto manual ({len(manual_texts)} exemplos):\n")
        f.write(f"  Acurácia: {manual_acc:.2%}\n")
        f.write(f"  Falsos positivos: {len(false_positives)}\n")
        f.write(f"  Falsos negativos: {len(false_negatives)}\n\n")
        f.write("Métricas por classe:\n")
        for cls, m in per_class.items():
            f.write(f"  {cls:25s} P={m['precision']:.2f} R={m['recall']:.2f} F1={m['f1']:.2f} (n={m['support']})\n")

    print(f"\n✅ Relatório salvo em:")
    print(f"   {json_path}")
    print(f"   {txt_path}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Avalia o classificador ML do dIscovery")
    parser.add_argument("--model", default="logreg", choices=["logreg", "naive_bayes"])
    args = parser.parse_args()
    run_evaluation(args.model)
