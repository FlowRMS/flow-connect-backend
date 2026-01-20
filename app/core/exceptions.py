class FlowAIError(Exception):
    pass


class NotFoundError(FlowAIError):
    pass


class UnauthorizedError(FlowAIError):
    pass


class ExpiredTokenError(UnauthorizedError):
    pass


class DuplicateRowError(FlowAIError):
    pass


class OutsideRepsRequiredError(FlowAIError):
    pass
