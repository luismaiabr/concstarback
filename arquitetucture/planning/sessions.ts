import { z } from 'zod';

/**
 * Schema das Sessões e Votos (Session Schema)
 * Define a estrutura para agendamentos e propostas de novos horários.
 */
export const SessionSchema = z.object({
  id: z.string()
    .uuid()
    .describe('ID único do registro de sessão (UUID v4)'),

  date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato deve ser YYYY-MM-DD')
    .describe('Data da sessão'),

  checkInStartTime: z.string()
    .regex(/^\d{2}:\d{2}$/, 'Formato deve ser HH:mm')
    .describe('Horário de início/sugerido'),

  isCustomStartTime: z.boolean()
    .describe('Se for false, é o horário padrão. Se true, é um voto de customização.'),

  user: z.string()
    .describe('Identificador do usuário que propôs/votou, ou "system" para o padrão.'),
});

export type Session = z.infer<typeof SessionSchema>;

/**
 * Classe que representa a Sessão
 */
export class SessionItem implements Session {
  id: string;
  date: string;
  checkInStartTime: string;
  isCustomStartTime: boolean;
  user: string;

  constructor(data: unknown) {
    const validatedData = SessionSchema.parse(data);
    this.id = validatedData.id;
    this.date = validatedData.date;
    this.checkInStartTime = validatedData.checkInStartTime;
    this.isCustomStartTime = validatedData.isCustomStartTime;
    this.user = validatedData.user;
  }
}
