import { z } from 'zod';

/**
 * Schema do Registro de Questões (Question Record Schema)
 * Define a estrutura de dados para o registro de uma bateria de questões resolvidas.
 */
export const QuestionRecordSchema = z.object({
  userId: z.string()
    .describe('ID único do usuário que registrou a bateria de questões'),

  date: z.string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato deve ser YYYY-MM-DD')
    .describe('Data do registro das questões'),

  time: z.string()
    .regex(/^\d{2}:\d{2}$/, 'Formato deve ser HH:mm')
    .describe('Hora do registro das questões'),

  description: z.string()
    .min(1)
    .describe('Descrição textual das questões resolvidas'),

  questionsCount: z.number()
    .int()
    .nonnegative()
    .describe('Quantidade total de questões resolvidas'),
});

export type QuestionRecord = z.infer<typeof QuestionRecordSchema>;

/**
 * Classe que representa o Registro de Questões, validando os dados no momento da instanciação.
 */
export class QuestionRecordItem implements QuestionRecord {
  userId: string;
  date: string;
  time: string;
  description: string;
  questionsCount: number;

  constructor(data: unknown) {
    const validatedData = QuestionRecordSchema.parse(data);
    this.userId = validatedData.userId;
    this.date = validatedData.date;
    this.time = validatedData.time;
    this.description = validatedData.description;
    this.questionsCount = validatedData.questionsCount;
  }
}
