#include <cs50.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>

int main(void)
{

    ////////// 01. Check for if card is valid //////////

    string card_num = get_string("Number: ");

    int position, even_sum = 0, odd_sum = 0;
    int length = strlen(card_num);

    for (position = 0; position < length; position ++)
    {

        // pick the number on the position (start from right)
        int num = atol(card_num) % (long)pow(10, position + 1) / (long)pow(10, position);

        // for ODD numbers (first and subsequent)
        if (position % 2 == 0)
        {
            odd_sum += num;
        }

        // for EVEN numbers (second and subsequent)
        else
        {
            num *= 2;
            if (num >= 10)
            {
                even_sum += num % 10; // digit
                even_sum += (int)(num / 10); // tens digit
            }
            else
            {
                even_sum += num;
            }
        }
    }

    if ((odd_sum + even_sum) % 10 != 0)
    {
        printf("INVALID\n");
        return 0;
    }


    ////////// 02. Check for the card type //////////

    int first_number = atol(card_num) / (long)pow(10, length - 1) % 10;
    int second_number = atol(card_num) / (long)pow(10, length - 2) % 10;

    if (length == 15 && first_number == 3)
    {
        if (second_number == 4 || second_number == 7)
        {
            printf("AMEX\n");
            return 0;
        }
    }
    else if (first_number == 4)
    {
        if (length == 13 || length == 16)
        {
            printf("VISA\n");
            return 0;
        }
    }
    else if (length == 16 && first_number == 5)
    {
        if (second_number >= 1 && second_number <= 5)
        {
            printf("MASTERCARD\n");
            return 0;
        }
    }

    printf("INVALID\n");
}