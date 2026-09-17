function QuestionInput({ question, onQuestionChange }) {
  const maxLength = 500

  const handleChange = (event) => {
    onQuestionChange(event.target.value)
  }

  return (
    <div className="question-field">
      <label htmlFor="question">Technical Question</label>

      <textarea
        id="question"
        value={question}
        onChange={handleChange}
        placeholder="e.g. How do I configure middleware for rate limiting?"
        rows="4"
        maxLength={maxLength}
      />

      <div className="question-footer">
        <div className="question-hint">
          Answers are grounded exclusively in official documentation for the
          selected version.
        </div>

        <span className="character-count">
          {question.length}/{maxLength}
        </span>
      </div>
    </div>
  )
}

export default QuestionInput