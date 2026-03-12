from src.dependencies.db_client import weather_table


def get_record(date: str) -> dict | None:

    response = weather_table.get_item(Key={"Date": date})
    return response.get("Item")

def put_record(record: dict) -> None:
    weather_table.put_item(Item=record)


def update_record(date: str, updates: dict) -> None:
    update_expression = "SET " + ", ".join(
        f"#k{i} = :v{i}" for i in range(len(updates))
    )
    expression_names = {f"#k{i}": k for i, k in enumerate(updates.keys())}
    expression_values = {f":v{i}": v for i, v in enumerate(updates.values())}

    weather_table.update_item(
        Key={"date": date},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values
    )


def delete_record(date: str) -> None:
    weather_table.delete_item(Key={"date": date})