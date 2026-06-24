import { z } from 'zod';

/**
 * Inspiration: Pydantic 2
 * Zod is the most adequate technology for TypeScript/Angular to provide
 * runtime validation and static type inference, similar to Pydantic in Python.
 */

// Enum defining possible types of settings
export const SettingTypeSchema = z.enum([
  'TIME',
  'STRING',
  'NUMBER',
  'BOOLEAN',
  'OPTIONS'
]);

export type SettingType = z.infer<typeof SettingTypeSchema>;

/**
 * General purpose setting validation schema
 * Defines a setting with its name, type, selected configuration, enums, and complementary value.
 */
export const GeneralSettingSchema = z.object({
  name: z.string()
    .describe("O nome do setting (ex: 'Horário de Check-in')"),
  
  type: SettingTypeSchema
    .describe("O tipo do setting"),
  
  selectedConfiguration: z.union([z.string(), z.number(), z.boolean(), z.null()])
    .describe("A configuração escolhida pelo usuário"),
  
  enums: z.array(z.union([z.string(), z.number()]))
    .optional()
    .describe("Lista de opções disponíveis caso o tipo seja de múltipla escolha (enums)"),
  
  value: z.any()
    .optional()
    .describe("Valores complementares para essa configuração (ex: metadados, regras de validação extra)")
});

export type GeneralSetting = z.infer<typeof GeneralSettingSchema>;

/**
 * Application Settings Table / Schema
 * Contains specific configurations like check-in time and timer start time.
 */
export const ApplicationSettingsTableSchema = z.object({
  checkinAvailableTime: GeneralSettingSchema.extend({
    name: z.literal('checkinAvailableTime'),
    type: z.literal('TIME')
  }),
  
  timerStartTime: GeneralSettingSchema.extend({
    name: z.literal('timerStartTime'),
    type: z.literal('TIME')
  })
});

export type ApplicationSettingsTable = z.infer<typeof ApplicationSettingsTableSchema>;

/**
 * Exemplo de classe de propósito geral que implementa a interface validada.
 */
export class AppSettingItem implements GeneralSetting {
  name: string;
  type: SettingType;
  selectedConfiguration: string | number | boolean | null;
  enums?: (string | number)[];
  value?: any;

  constructor(data: unknown) {
    // Valida os dados no momento da instância, semelhante ao Pydantic
    const validatedData = GeneralSettingSchema.parse(data);
    this.name = validatedData.name;
    this.type = validatedData.type;
    this.selectedConfiguration = validatedData.selectedConfiguration;
    this.enums = validatedData.enums;
    this.value = validatedData.value;
  }
}
