import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./Select"

export function SelectHero() {
  const data = [
    {
      value: "dress-shirt-striped",
      label: "Striped Dress Shirt",
    },
    {
      value: "relaxed-button-down",
      label: "Relaxed Fit Button Down",
    },
    {
      value: "slim-button-down",
      label: "Slim Fit Button Down",
    },
    {
      value: "dress-shirt-solid",
      label: "Solid Dress Shirt",
    },
    {
      value: "dress-shirt-check",
      label: "Check Dress Shirt",
    },
  ]

  return (
    <Select>
      <SelectTrigger>
        <SelectValue placeholder="Select" />
      </SelectTrigger>
      <SelectContent>
        {data.map((item) => (
          <SelectItem key={item.value} value={item.value}>
            {item.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}