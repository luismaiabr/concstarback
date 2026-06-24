import { z } from 'zod';

/**
 * Schema do Usuário Online (Online User Schema)
 * Define a estrutura de dados simples de um usuário online na sessão de estudos.
 */
export const OnlineUserSchema = z.object({
  name: z.string()
    .min(1)
    .describe('Nome do usuário online na sessão'),

  profileUrl: z.string()
    .url()
    .describe('URL do perfil do usuário online'),
});

export type OnlineUser = z.infer<typeof OnlineUserSchema>;

/**
 * Classe que representa o Usuário Online, validando os dados no momento da instanciação.
 */
export class OnlineUserItem implements OnlineUser {
  name: string;
  profileUrl: string;

  constructor(data: unknown) {
    const validatedData = OnlineUserSchema.parse(data);
    this.name = validatedData.name;
    this.profileUrl = validatedData.profileUrl;
  }
}
