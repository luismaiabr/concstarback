import { z } from 'zod';

/**
 * Schema do Usuário (User Schema)
 * Define a estrutura de dados de um usuário contendo perfil básico e
 * chaves estrangeiras de relacionamento com outras tabelas do sistema.
 */
export const UserSchema = z.object({
  id: z.string()
    .uuid()
    .describe('ID único do usuário (UUID v4)'),

  name: z.string()
    .min(1)
    .describe('Nome completo do usuário'),

  email: z.string()
    .email()
    .describe('Endereço de e-mail do usuário'),

  profilePhotoUrl: z.string()
    .url()
    .describe('URL pública da foto de perfil do usuário'),
});

export type User = z.infer<typeof UserSchema>;

/**
 * Classe que representa o Usuário, validando os dados fornecidos no momento
 * da instanciação (conceito similar ao Pydantic).
 */
export class UserItem implements User {
  id: string;
  name: string;
  email: string;
  profilePhotoUrl: string;

  constructor(data: unknown) {
    const validatedData = UserSchema.parse(data);
    this.id = validatedData.id;
    this.name = validatedData.name;
    this.email = validatedData.email;
    this.profilePhotoUrl = validatedData.profilePhotoUrl;
  }
}
