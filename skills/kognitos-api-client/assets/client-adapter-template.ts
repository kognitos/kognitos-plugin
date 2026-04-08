export interface KognitosRequest<TInput> {
  operation: string;
  input: TInput;
}

export interface KognitosResult<TOutput> {
  ok: boolean;
  data?: TOutput;
  error?: {
    code: string;
    message: string;
    retryable: boolean;
  };
}

export interface KognitosClient<TInput, TOutput> {
  execute(request: KognitosRequest<TInput>): Promise<KognitosResult<TOutput>>;
}
