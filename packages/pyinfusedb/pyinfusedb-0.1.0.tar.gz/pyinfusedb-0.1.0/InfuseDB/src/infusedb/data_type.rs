use std::usize;

// Written by Alberto Ruiz 2024-03-08
// The data type module will provide the data types for the InfuseDB
// this will be store several types of data, like text, numbers, dates, arrays and documents
//
// The data type will be used to store the data in the documents
use super::collection::Document;
use uuid::Uuid;

pub enum FindOp {
    Eq,
    NotEq,
    Gt,
    Lt,
}

#[derive(PartialEq, Debug)]
pub enum DataType {
    Id(Uuid),
    Text(String),
    Number(f32),
    Boolean(bool),
    Array(Vec<DataType>),
    Document(Document),
}

#[macro_export]
macro_rules! d {
    // Para arrays/vecs, aplica el macro recursivamente a cada elemento
    ([$( $elem:tt ),* $(,)?]) => {
        $crate::DataType::Array(vec![$( $crate::DataType::from($elem) ),*])
    };

    // Para expresiones simples, asume que hay un From<T> para DataType
    ($val:expr) => {
        $crate::DataType::from($val)
    };
}

impl DataType {
    pub fn get_type(&self) -> &str {
        match self {
            DataType::Id(_) => "id",
            DataType::Text(_) => "text",
            DataType::Number(_) => "number",
            DataType::Boolean(_) => "boolean",
            DataType::Array(_) => "array",
            DataType::Document(_) => "document",
        }
    }

    pub fn get(&self, index: &str) -> Option<&DataType> {
        match self {
            DataType::Array(v) => {
                let n = index.parse::<usize>().ok()?;
                v.get(n)
            }
            DataType::Document(d) => d.get(index),
            _ => None,
        }
    }

    pub fn get_mut(&mut self, index: &str) -> Option<&mut DataType> {
        match self {
            DataType::Array(v) => {
                let n = index.parse::<usize>().ok()?;
                v.get_mut(n)
            }
            DataType::Document(d) => d.get_mut(index),
            _ => None,
        }
    }

    pub fn find(&self, sub_key: &str, op: FindOp, value: DataType) -> Option<DataType> {
        let mut result: Vec<DataType> = Vec::new();
        match self {
            DataType::Array(v) => {
                for item in v {
                    let sub_item = item.get(sub_key);
                    if sub_item.is_none() {
                        continue;
                    }
                    let sub_item = sub_item.unwrap();
                    let items_are_number = matches!(value, DataType::Number(_))
                        && matches!(*sub_item, DataType::Number(_));
                    let matched = match op {
                        FindOp::Eq => *sub_item == value,
                        FindOp::NotEq => *sub_item != value,
                        FindOp::Gt => items_are_number && sub_item.to_number() > value.to_number(),
                        FindOp::Lt => items_are_number && sub_item.to_number() < value.to_number(),
                    };
                    if matched {
                        result.push(item.clone());
                    }
                }
                return Some(DataType::Array(result));
            }

            _ => None,
        }
    }

    pub fn set(&mut self, index: &str, dt: DataType) -> Result<DataType, &'static str> {
        match self {
            DataType::Array(vec) => {
                if let Ok(index) = index.parse::<usize>() {
                    while index >= vec.len() {
                        vec.push(DataType::Text("".to_string()));
                    }
                    vec[index] = dt;
                    Ok(self.clone())
                } else {
                    Err("Invalid index")
                }
            }
            DataType::Document(doc) => {
                doc.insert(index.to_string(), dt);
                Ok(self.clone())
            }
            _ => Err("Not supported"),
        }
    }
    pub fn remove(&mut self, index: &str) -> Result<DataType, &'static str> {
        match self {
            DataType::Array(vec) => {
                if let Ok(index) = index.parse::<usize>() {
                    vec.remove(index);
                    Ok(self.clone())
                } else {
                    Err("Invalid index")
                }
            }
            DataType::Document(doc) => {
                doc.remove(index);
                Ok(self.clone())
            }
            _ => Err("Not supported"),
        }
    }

    //add into
    pub fn to_id(&self) -> Uuid {
        match self {
            DataType::Id(id) => *id,
            _ => panic!("Not an ID"),
        }
    }
    pub fn to_text(&self) -> &String {
        match self {
            DataType::Text(text) => text,
            _ => panic!("Not a Text"),
        }
    }
    pub fn to_number(&self) -> f32 {
        match self {
            DataType::Number(number) => *number,
            _ => panic!("Not a Number"),
        }
    }
    pub fn to_boolean(&self) -> bool {
        match self {
            DataType::Boolean(boolean) => *boolean,
            _ => panic!("Not a Boolean"),
        }
    }
    pub fn to_array(&self) -> &Vec<DataType> {
        match self {
            DataType::Array(array) => array,
            _ => panic!("Not an Array"),
        }
    }
    pub fn to_document(&self) -> &Document {
        match self {
            DataType::Document(document) => document,
            _ => panic!("Not a Document"),
        }
    }

    pub fn infer_type(raw: &str) -> u16 {
        let raw = raw.trim();
        if Uuid::parse_str(raw).is_ok() {
            1
        } else if raw.parse::<f32>().is_ok() {
            3
        } else if raw.to_lowercase().as_str() == "true" || raw.to_lowercase().as_str() == "false" {
            4
        } else if raw.starts_with('[') && raw.ends_with(']') {
            5
        } else if raw.starts_with('{') && raw.ends_with('}') {
            6
        } else {
            2
        }
    }

    pub fn load(t: u16, raw: String) -> Option<Self> {
        let raw = raw.trim().to_string();
        match t {
            1 => {
                let id = Uuid::parse_str(raw.as_str());
                if id.is_err() {
                    return None;
                }
                Some(DataType::Id(id.unwrap()))
            }
            2 => Some(DataType::Text(raw.trim_matches('"').to_string())),
            3 => {
                let n = raw.parse::<f32>();
                if n.is_err() {
                    return None;
                }
                Some(DataType::Number(n.unwrap()))
            }
            4 => match raw.to_lowercase().as_str() {
                "true" => Some(DataType::Boolean(true)),
                "false" => Some(DataType::Boolean(false)),
                _ => None,
            },
            5 => {
                let mut new_vec = Vec::new();
                let raw = raw.strip_suffix(']').unwrap().strip_prefix('[').unwrap();
                let mut open_array = false;
                let mut open_string = false;
                let mut open_bracket = 0;

                let mut sub_raw = String::new();
                for chr in raw.chars() {
                    if chr == ',' && !open_array && !open_string && open_bracket == 0 {
                        let t = Self::infer_type(&sub_raw);
                        let r = Self::load(t, sub_raw.clone());
                        if r.is_some() {
                            new_vec.push(r.unwrap());
                            sub_raw = String::new();
                            continue;
                        }
                    }
                    if chr == '[' && !open_array {
                        open_array = true;
                    }
                    if chr == ']' && open_array {
                        open_array = false;
                    }
                    if chr == '{' {
                        open_bracket += 1;
                    }
                    if chr == '}' {
                        open_bracket -= 1;
                    }
                    if chr == '"' {
                        open_string = !open_string
                    }
                    sub_raw.push(chr);
                }
                if !sub_raw.is_empty() {
                    let t = Self::infer_type(&sub_raw);
                    let r = Self::load(t, sub_raw.clone());
                    if r.is_some() {
                        new_vec.push(r.unwrap());
                    }
                }

                Some(DataType::Array(new_vec))
            }
            6 => {
                let mut d = Document::new();
                let raw = raw.strip_suffix('}').unwrap().strip_prefix('{').unwrap();
                let mut key = String::new();
                let mut key_done = false;
                let mut open_array = 0;
                let mut open_string = false;
                let mut open_bracket = 0;
                let mut value = String::new();
                for chr in raw.chars() {
                    if chr == ':' && !key_done {
                        key_done = true;
                        continue;
                    }
                    if key_done {
                        if chr == ',' && open_array == 0 && !open_string && open_bracket == 0 {
                            let t = Self::infer_type(&value);
                            let r = Self::load(t, value.clone());
                            if r.is_some() {
                                d.insert(key.trim().to_string(), r.unwrap());
                                key = String::new();
                                value = String::new();
                                key_done = false;
                                continue;
                            }
                        }

                        if chr == '[' {
                            open_array += 1;
                        }
                        if chr == ']' {
                            open_array -= 1;
                        }
                        if chr == '{' {
                            open_bracket += 1;
                        }
                        if chr == '}' {
                            open_bracket -= 1
                        }
                        if chr == '"' {
                            open_string = !open_string
                        }

                        value.push(chr);
                    } else {
                        key.push(chr);
                    }
                }
                if !key.is_empty() && !value.is_empty() {
                    let t = Self::infer_type(&value);
                    let r = Self::load(t, value.clone());
                    if r.is_some() {
                        d.insert(key.trim().to_string(), r.unwrap());
                    }
                }
                Some(DataType::Document(d))
            }
            _ => None,
        }
    }
}

impl ToString for DataType {
    fn to_string(&self) -> String {
        match self {
            DataType::Id(id) => id.to_string(),
            DataType::Text(text) => format!("\"{}\"", text.to_string()),
            DataType::Number(number) => number.to_string(),
            DataType::Boolean(boolean) => boolean.to_string(),
            DataType::Array(array) => {
                let mut result = String::new();
                result.push('[');
                for value in array {
                    result.push_str(&value.to_string());
                    result.push_str(", ");
                }
                let mut result = result.strip_suffix(", ").unwrap_or(&result).to_string();
                result.push(']');
                result
            }
            DataType::Document(document) => {
                let mut result = String::new();
                result.push('{');
                for (key, value) in document {
                    result.push_str(&key);
                    result.push_str(": ");
                    result.push_str(&value.to_string());
                    result.push_str(", ");
                }
                result.pop();
                result.pop();
                result.push('}');

                result
            }
        }
    }
}

impl From<Uuid> for DataType {
    fn from(value: Uuid) -> Self {
        DataType::Id(value)
    }
}

impl From<String> for DataType {
    fn from(value: String) -> Self {
        DataType::Text(value)
    }
}

impl From<&str> for DataType {
    fn from(value: &str) -> Self {
        DataType::Text(value.to_string())
    }
}

impl From<f32> for DataType {
    fn from(value: f32) -> Self {
        DataType::Number(value)
    }
}

impl From<i32> for DataType {
    fn from(value: i32) -> Self {
        DataType::Number(value as f32)
    }
}

impl From<bool> for DataType {
    fn from(value: bool) -> Self {
        DataType::Boolean(value)
    }
}

impl From<Vec<DataType>> for DataType {
    fn from(value: Vec<DataType>) -> Self {
        DataType::Array(value)
    }
}

impl From<Document> for DataType {
    fn from(value: Document) -> Self {
        DataType::Document(value)
    }
}

//impl clone
impl Clone for DataType {
    fn clone(&self) -> Self {
        match self {
            DataType::Id(id) => DataType::Id(*id),
            DataType::Text(text) => DataType::Text(text.clone()),
            DataType::Number(number) => DataType::Number(*number),
            DataType::Boolean(boolean) => DataType::Boolean(*boolean),
            DataType::Array(array) => DataType::Array(array.clone()),
            DataType::Document(document) => DataType::Document(document.clone()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::DataType;

    #[test]
    fn test_macro() {
        let dd = d!("Hello");
        let expected = DataType::from("Hello");
        assert!(dd == expected);
        let dd = d!(10);
        let expected = DataType::from(10);
        assert!(dd == expected);
        let dd = d!(["hello", 10]);
        let expected = DataType::from(vec![d!("hello"), d!(10)]);
        assert!(dd == expected);
    }
}
