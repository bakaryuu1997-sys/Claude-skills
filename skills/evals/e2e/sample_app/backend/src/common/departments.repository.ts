import { Injectable } from '@nestjs/common';

export interface Department {
  id: string;
  name: string;
}

@Injectable()
export class DepartmentsRepository {
  private readonly items = new Map<string, Department>();

  add(d: Department): void {
    this.items.set(d.id, d);
  }

  findById(id: string): Department | undefined {
    return this.items.get(id);
  }
}
