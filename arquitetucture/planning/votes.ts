import { z } from 'zod';

/**
 * Schema do Voto de Horário (Vote Schema)
 * Define a estrutura de dados de um voto individual para um horário customizado.
 */
export const VoteSchema = z.object({
  date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato deve ser YYYY-MM-DD')
    .describe('Data da sessão na qual o voto foi registrado'),

  time: z.string()
    .regex(/^\d{2}:\d{2}$/, 'Formato deve ser HH:mm')
    .describe('Horário sugerido pelo voto'),

  userId: z.string()
    .describe('ID único do usuário que registrou o voto'),
});

export type Vote = z.infer<typeof VoteSchema>;

/**
 * Classe que representa o Voto, validando os dados no momento da instanciação.
 */
export class VoteItem implements Vote {
  date: string;
  time: string;
  userId: string;

  constructor(data: unknown) {
    const validatedData = VoteSchema.parse(data);
    this.date = validatedData.date;
    this.time = validatedData.time;
    this.userId = validatedData.userId;
  }
}
