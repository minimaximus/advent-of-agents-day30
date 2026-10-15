# Enterprise certificate proxies can interfere with mTLS on managed workstations.
export GOOGLE_API_USE_CLIENT_CERTIFICATE := false
export GOOGLE_API_USE_MTLS := never

.PHONY: help eval kata explain fix reset aqua dry-run playground clean hillclimb-fix hillclimb-reset

help: ## Show available Halloween Continuous Alignment & AQuA Kata targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

eval: ## Act I (Pre-Deploy Gate): Run candy_auditor on Golden Dataset, grade policy compliance, enforce Mean >= 4.0
	python3 -m eval_harness.run_hillclimb

kata: ## Act I (Fast <2s Rehearsal): Run Pre-Deploy Golden-Dataset Policy Compliance Gate locally
	python3 -m eval_harness.run_hillclimb --fast

explain: ## Act I (Diagnose): Print Gemini Judge rationales for any house breaching policy (Score <= 4.0)
	python3 -m eval_harness.explain_criteria_results --max_score_to_show 4.0

fix: ## Act II (Align): Restore policy compliance rules in SKILL.md files (and display diff)
	python3 -m eval_harness.lab_skills fix

reset: ## Reset SKILL.md files back to the regressed baseline (for re-recording)
	python3 -m eval_harness.lab_skills reset

aqua: ## Act III (Post-Deploy Continuous Alignment): Run AQuA 9-question session review, cluster verification & RCA
	python3 -m eval_harness.run_aqua

dry-run: ## Preview the compiled PointwiseMetricPromptTemplate sent to the LLM Judge
	python3 -m eval_harness.run_geap_eval --dry-run --out runs/dry_run/geap_prompt_preview.json

playground: ## Launch ADK Web UI to chat with candy_auditor and inspect EvalSet traces
	adk web

clean: ## Remove generated runs and reset skills to regressed baseline
	rm -rf runs/hillclimb_* candy_auditor/hillclimb_*.evalset.json
	python3 -m eval_harness.lab_skills reset

# Legacy aliases kept for backwards compatibility
hillclimb-fix: fix
hillclimb-reset: reset
