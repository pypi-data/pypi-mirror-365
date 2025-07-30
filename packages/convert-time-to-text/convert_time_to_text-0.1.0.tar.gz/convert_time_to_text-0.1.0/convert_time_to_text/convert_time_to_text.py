def convert_time_to_text(h, m):
    error_message = 'Error : Please provide integer values.'

    if not isinstance(h, int) or not isinstance(m, int):
        print(error_message)
        return error_message

    h = h % 12
    m = m % 60

    number_array = [
        '',
        'one',
        'two',
        'three',
        'four',
        'five',
        'six',
        'seven',
        'eight',
        'nine',
        'ten',
        'eleven',
        'twelve',
        'thirteen',
        'fourteen',
        'fifteen',
        'sixteen',
        'seventeen',
        'eighteen',
        'nineteen',
        'twenty'
    ]

    temp_m = m
    hour_string = number_array[h] if h > 0 else number_array[12]
    minute_string = None
    time_text = ''
    time_text_substring = "to"

    if m == 0:
        time_text = f"{hour_string} o' clock"
    elif m == 15:
        time_text = f"quarter past {hour_string}"
    elif m == 30:
        time_text = f"half past {hour_string}"
    elif m == 45:
        time_text = f"quarter to {number_array[h + 1]}"
    else:
        if m > 30:
            temp_m = 60 - m
            hour_string = number_array[h + 1]
        
        if temp_m <= 20:
            temp_m_text = number_array[temp_m]
        else:
            tens = (temp_m // 10) * 10
            units = temp_m % 10
            temp_m_text = number_array[tens] + ' ' + number_array[units] if units else number_array[tens]

        temp_m_text += ' minute'
        if temp_m != 1:
            temp_m_text += 's'

        if m > 30:
            time_text = f"{temp_m_text} to {hour_string}"
        else:
            time_text = f"{temp_m_text} past {hour_string}"

    return time_text


# print(convert_time_to_text(5,00))
# print(convert_time_to_text(5,0))
# print(convert_time_to_text(5,1))
# print(convert_time_to_text(5,9))
# print(convert_time_to_text(5,10))
# print(convert_time_to_text(5,15))
# print(convert_time_to_text(5,30))
# print(convert_time_to_text(5,37))
# print(convert_time_to_text(5,40))
# print(convert_time_to_text(5,45))
# print(convert_time_to_text(5,47))
# print(convert_time_to_text(12,24))
# print(convert_time_to_text(11,50))
# print(convert_time_to_text(12,50))
# print(convert_time_to_text(12,20))
