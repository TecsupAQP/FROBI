from frobi.shared.domain import DomainError, ErrorKind

MAX_QUESTION_CHARS = 2000


class EmptyQuestion(DomainError):
    code = "Assistant.EmptyQuestion"
    kind = ErrorKind.VALIDATION
    default_message = "Escribe tu pregunta."


class QuestionTooLong(DomainError):
    code = "Assistant.QuestionTooLong"
    kind = ErrorKind.VALIDATION
    default_message = f"Tu pregunta supera los {MAX_QUESTION_CHARS} caracteres. Acórtala un poco."


class ConversationFull(DomainError):
    code = "Assistant.ConversationFull"
    kind = ErrorKind.CONFLICT
    default_message = "Esta conversación llegó a su límite. Empieza una nueva para seguir."


class TooManyQuestions(DomainError):
    code = "Assistant.TooManyQuestions"
    kind = ErrorKind.CONFLICT
    default_message = "Hiciste muchas preguntas seguidas. Espera un minuto y vuelve a intentarlo."


class StillAnswering(DomainError):
    code = "Assistant.StillAnswering"
    kind = ErrorKind.CONFLICT
    default_message = "Todavía estoy respondiendo tu pregunta anterior. Espera a que termine."
