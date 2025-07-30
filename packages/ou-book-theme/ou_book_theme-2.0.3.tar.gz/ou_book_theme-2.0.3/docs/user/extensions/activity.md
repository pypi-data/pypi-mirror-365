# Activity-related

The `{activity}` and `{activity-answer}` blocks can be used to mark up activities and answers
associated with those activities.

## Activity

The `{activity}` marks out a piece of practical work that is undertaken by the student:

::::{code-block} markdown
:::{activity} Activity 1

This is an activity that you can undertake in your own time.
:::
::::

:::{activity} Activity 1

This is an activity that you can undertake in your own time.
:::

## Answer

Optionally the activity can be provided with an answer that is initially hidden:

:::::{code-block} markdown
::::{activity} Activity 2

This is an activity you should undertake on your own, but we have also provided an answer.

:::{activity-answer}
This is a sample answer for the activity, which the user can show by clicking on the link.
:::
::::
:::::

::::{activity} Activity 2

This is an activity you should undertake on your own, but we have also provided an answer.

:::{activity-answer}
This is a sample answer for the activity, which the user can show by clicking on the link.
:::
::::
