document.addEventListener('DOMContentLoaded', () => {
    // Create Rule Form Submission
    document.getElementById('create-rule-form').onsubmit = async function (e) {
        e.preventDefault();
        const ruleName = document.getElementById('rule-name').value;
        const ruleString = document.getElementById('rule-string').value;

        const response = await fetch('/create_rule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: ruleName, rule_string: ruleString })
        });
        const result = await response.json();
        document.getElementById('create-rule-response').innerText = JSON.stringify(result, null, 2);
    };

    // Combine Rules Form Submission
    document.getElementById('combine-rules-form').onsubmit = async function (e) {
        e.preventDefault();
        const rules = document.getElementById('combine-rules-input').value.split(',');
        const operators = document.getElementById('combine-operators-input').value.split(',');

        const response = await fetch('/combine_rules', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rules: rules, operators: operators })
        });
        const result = await response.json();
        document.getElementById('combine-rules-response').innerText = JSON.stringify(result, null, 2);
    };

    // Evaluate Rule Form Submission
    document.getElementById('evaluate-rule-form').onsubmit = async function (e) {
        e.preventDefault();
        const combinedAst = JSON.parse(document.getElementById('combined-ast-input').value);
        const userData = JSON.parse(document.getElementById('user-data-input').value);

        const response = await fetch('/evaluate_rule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ combined_ast: combinedAst, user_data: userData })
        });
        const result = await response.json();
        document.getElementById('evaluate-rule-response').innerText = JSON.stringify(result, null, 2);
    };
});