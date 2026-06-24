import { z } from 'zod';

/**
 * Schema do Cancelamento de Sessão (Cancellation Schema)
 * Define a estrutura de dados para o cancelamento de uma sessão de estudos.
 */
export const CancellationSchema = z.object({
  userId: z.string()
    .describe('ID único do usuário que cancelou a sessão'),

  date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato deve ser YYYY-MM-DD')
    .describe('Data da sessão cancelada'),

  reason: z.string()
    .min(1)
    .describe('Motivo que justifica o cancelamento da sessão'),
});

export type Cancellation = z.infer<typeof CancellationSchema>;

/**
 * Classe que representa o Cancelamento, validando os dados no momento da instanciação.
 */
export class CancellationItem implements Cancellation {
  userId: string;
  date: string;
  reason: string;

  constructor(data: unknown) {
    const validatedData = CancellationSchema.parse(data);
    this.userId = validatedData.userId;
    this.date = validatedData.date;
    this.reason = validatedData.reason;
  }
}
