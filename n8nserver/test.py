# Loop over input items and add a new field called 'myNewField' to the JSON of each one
my_op = "{\"messages\": [{\"role\": \"user\", \"content\": \"hi!\"}, {\"role\": \"user\", \"content\": \"hey there how are you?\"}]}"
sys_op = "{\"messages\": [{\"role\": \"user\", \"content\": \"hi!\"}, {\"role\": \"user\", \"content\": \"hey there how are you?\"}]}"
if(my_op == sys_op):
    print("yes")