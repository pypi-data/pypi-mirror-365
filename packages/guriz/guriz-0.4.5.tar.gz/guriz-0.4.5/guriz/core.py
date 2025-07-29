from .SQL.connection import MySQL
from rich.console import Console
from typing import Any

console = Console()

def mysql_to_python(mysql_type: str) -> str:
    mysql_type = mysql_type.lower()
    if "int" in mysql_type:
        return "int"
    if "decimal" in mysql_type or "float" in mysql_type or "double" in mysql_type:
        return "float"
    if "bool" in mysql_type or "tinyint(1)" in mysql_type:
        return "bool"
    if "date" in mysql_type or "time" in mysql_type or "year" in mysql_type:
        return "datetime"
    return "str"


def pull_models(output: str) -> bool:
    try:
        tables = MySQL.execute_select("SHOW TABLES", fetch_type='all')
        table_names = [list(t.values())[0] for t in tables]

        relations = MySQL.execute_select(f"""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE 
                TABLE_SCHEMA = DATABASE()
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """, fetch_type='all')

        relations_by_table: dict[str, Any] = {}
        for rel in relations:
            table = rel["TABLE_NAME"]
            relations_by_table.setdefault(table, []).append(rel)

        with open(output, "w") as f:
            f.write("from __future__ import annotations\n")
            f.write("from dataclasses import dataclass\n")
            f.write("from typing import ClassVar\n")
            f.write("from guriz.repository_protocol import RepositoryProtocol\n\n")

            for table in table_names:
                console.print(f"[bold blue]Gerando modelo para tabela:[/] {table}")
                columns = MySQL.execute_select(f"SHOW COLUMNS FROM `{table}`", fetch_type='all')
                table_relations = relations_by_table.get(table, [])

                safe_table = table.replace("-", "_")
                class_name = safe_table.title().replace("_", "")
                f.write(f"@dataclass\n")
                f.write(f"class {class_name}(RepositoryProtocol['{class_name}']):\n")
                f.write(f"    __tablename__ = '{table}'\n\n")

                for col in columns:
                    field_name = col["Field"]
                    const_name = field_name.upper().replace("-", "_")
                    f.write(f"    {const_name}: ClassVar[str] = \"{field_name}\"\n")                

                f.write("\n")
        return True
    except Exception as e:
        console.print(f"[red]Erro ao puxar modelos:[/] {e}")
        return False
    
def pull_models_for_pydantic(output: str) -> bool:
    try:
        tables = MySQL.execute_select("SHOW TABLES", fetch_type='all')
        table_names = [list(t.values())[0] for t in tables]

        relations = MySQL.execute_select(f"""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE 
                TABLE_SCHEMA = DATABASE()
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """, fetch_type='all')

        relations_by_table: dict[str, Any] = {}
        for rel in relations:
            table = rel["TABLE_NAME"]
            relations_by_table.setdefault(table, []).append(rel)

        with open(output, "w") as f:
            f.write("from __future__ import annotations\n")
            f.write("from dataclasses import dataclass\n")
            f.write("from typing import ClassVar\n\n")

            for table in table_names:
                console.print(f"[bold blue]Gerando modelo para tabela:[/] {table}")
                columns = MySQL.execute_select(f"SHOW COLUMNS FROM `{table}`", fetch_type='all')
                table_relations = relations_by_table.get(table, [])

                safe_table = table.replace("-", "_")
                class_name = safe_table.title().replace("_", "")
                f.write(f"@dataclass\n")
                f.write(f"class {class_name}:\n")
                f.write(f"    __tablename__ = '{table}'\n\n")

                for col in columns:
                    field_name = col["Field"]
                    const_name = field_name.upper().replace("-", "_")
                    f.write(f"    {const_name}: ClassVar[str] = \"{field_name}\"\n")

                f.write("\n")

        with open("models_response.py", "w") as f:
            f.write("from pydantic import BaseModel\n\n")

            for table in table_names:
                safe_table = table.replace("-", "_")
                class_name = safe_table.title().replace("_", "")
                columns = MySQL.execute_select(f"SHOW COLUMNS FROM `{table}`", fetch_type='all')

                f.write(f"class {class_name}Response(BaseModel):\n")
                for col in columns:
                    field = col["Field"]
                    sql_type = col["Type"]

                    if "int" in sql_type:
                        ftype = "int"
                    elif "char" in sql_type or "text" in sql_type:
                        ftype = "str"
                    elif "decimal" in sql_type or "float" in sql_type:
                        ftype = "float"
                    elif "bool" in sql_type:
                        ftype = "bool"
                    else:
                        ftype = "str"

                    f.write(f"    {field}: {ftype} | None = None\n")
                f.write("\n")

        return True
    except Exception as e:
        console.print(f"[red]Erro ao puxar modelos:[/] {e}")
        return False
