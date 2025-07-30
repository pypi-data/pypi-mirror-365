; ---------------------------------------------------------------------------
;  Strudel syntax-highlighting rules
; ---------------------------------------------------------------------------
;  CAPTURE NAMING
;  1.  Specific > generic – put the most specific patterns first.
;  2.  Use the standard highlight names recognised by tree-sitter-highlight[10].
; ---------------------------------------------------------------------------

; ──────────────────────────────────────────────────────────────────────────
; Keywords
; ──────────────────────────────────────────────────────────────────────────
"var"            @keyword             ; variable declaration
"let"            @keyword
"const"          @keyword
"$:"             @keyword             ; default assignment prefix

; ──────────────────────────────────────────────────────────────────────────
; Punctuation & Operators
; ──────────────────────────────────────────────────────────────────────────
"="              @operator
"."              @punctuation.delimiter
","              @punctuation.delimiter
":"              @punctuation.delimiter
";"              @punctuation.delimiter
"("              @punctuation.bracket
")"              @punctuation.bracket

; ──────────────────────────────────────────────────────────────────────────
; Arithmetic Operators (Binary Expressions)
; ──────────────────────────────────────────────────────────────────────────
; Capture arithmetic operators from binary expressions
(additive_expression
  operator: _ @operator)

(multiplicative_expression
  operator: _ @operator)

; Alternative approach - directly capture operator literals
"+"              @operator
"-"              @operator
"*"              @operator
"/"              @operator

; ──────────────────────────────────────────────────────────────────────────
; Literals
; ──────────────────────────────────────────────────────────────────────────
(string)         @string
(number)         @number
(comment)        @comment

; ──────────────────────────────────────────────────────────────────────────
; Identifiers
; ──────────────────────────────────────────────────────────────────────────
; 1. Function call identifiers
(function_call
  (identifier)   @function.call)

; 2. Method call identifiers (after the dot)
(method_call
  (identifier)   @function.method)

; 3. Variable declarations: names on the LHS
(variable_declarator
  name: (identifier) @variable)

; 4. All remaining identifiers default to variable
(identifier)     @variable

; ──────────────────────────────────────────────────────────────────────────
; Expressions & Chains
; ──────────────────────────────────────────────────────────────────────────
; Highlight the leading identifier of a chained method sequence
(chained_method
  (_
    .
    (identifier) @function.method))

; ──────────────────────────────────────────────────────────────────────────
; Binary Expression Highlighting
; ──────────────────────────────────────────────────────────────────────────
; Highlight the entire binary expressions for context
(binary_expression) @expression

; Specific highlighting for additive and multiplicative expressions
(additive_expression) @expression.arithmetic
(multiplicative_expression) @expression.arithmetic
